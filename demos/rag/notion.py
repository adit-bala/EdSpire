import os, sys, json, argparse
from pathlib import Path
from notion_client import Client
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.storage import LocalFileStore
from langchain.embeddings.cache import CacheBackedEmbeddings
from langchain_community.vectorstores import FAISS

EMBEDDING_MODEL = "text-embedding-3-small"

# Parse command line arguments
parser = argparse.ArgumentParser(description='Notion RAG System')
parser.add_argument('--refresh', action='store_true', 
                    help='Refresh the FAISS index by re-processing Notion pages')
parser.add_argument('--chat-only', action='store_true',
                    help='Skip processing and go directly to chat (requires existing index)')
args = parser.parse_args()

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not (NOTION_TOKEN and OPENAI_API_KEY):
    sys.exit("❌  Environment variables NOTION_TOKEN and OPENAI_API_KEY must be set. Please export them first.")

notion = Client(auth=NOTION_TOKEN)

def iter_all_pages():
    cursor = None
    while True:
        print(f"Searching with cursor: {cursor}")
        resp = notion.search(
                    start_cursor=cursor, page_size=100)
        print(f"Got {len(resp['results'])} results, has_more: {resp.get('has_more')}")
        
        # Filter for pages in the results
        pages = [result for result in resp["results"] if result.get("object") == "page"]
        print(f"Found {len(pages)} pages")
        
        for page in pages:
            yield page
            
        if not resp.get("has_more"):
            break
        cursor = resp["next_cursor"]

def print_title(page_obj, depth):
    """Pretty-print the page title with indentation."""
    title = "Untitled"
    for prop in page_obj.get("properties", {}).values():
        if prop.get("type") == "title" and prop["title"]:
            title = "".join(t["plain_text"] for t in prop["title"])
            break
    indent = "  " * depth
    print(f"{indent}- {title}  ({page_obj['id']})")

def traverse_page(page_id: str, depth: int = 0, max_pages: int = 5, counter=[0]):
    """
    DFS through page -> child_page / child_database blocks.
    Uses `counter` list to keep a mutable page count across recursion.
    """
    if counter[0] >= max_pages:
        return
    
    try:
        page_obj = notion.pages.retrieve(page_id=page_id)
        print_title(page_obj, depth)
        counter[0] += 1

        # Walk this page's blocks
        cursor = None
        while True:
            children = notion.blocks.children.list(
                block_id=page_id,
                start_cursor=cursor,
                page_size=100,
            )
            for block in children["results"]:
                b_type = block["type"]
                if b_type in ("child_page", "child_database"):
                    traverse_page(block["id"], depth + 1, max_pages, counter)
                    if counter[0] >= max_pages:
                        return
            if not children["has_more"]:
                break
            cursor = children["next_cursor"]
    except Exception as e:
        print(f"Error processing page {page_id}: {e}")

PERSIST_DIR = Path("faiss_index")
CACHE_DIR   = Path("emb_cache")
CHUNK_SIZE  = 800            # ≈ 200 tokens
CHUNK_OVER  = int(CHUNK_SIZE * 0.2)

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVER)

# Fixed: Use langchain_openai instead of langchain.embeddings
base_emb = OpenAIEmbeddings(model=EMBEDDING_MODEL, openai_api_key=OPENAI_API_KEY)
cache = LocalFileStore(str(CACHE_DIR))
emb = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings=base_emb, 
    document_embedding_cache=cache,
    namespace="notion_v1"
)

# Load or create FAISS index
if PERSIST_DIR.exists() and not args.refresh:
    try:
        vectordb = FAISS.load_local(str(PERSIST_DIR), emb, allow_dangerous_deserialization=True)
        print(f"✅  Loaded existing FAISS index with {vectordb.index.ntotal} vectors.")
        
        # If using chat-only mode, skip processing entirely
        if args.chat_only:
            print("💬  Chat-only mode: Skipping Notion processing...")
            skip_processing = True
        else:
            skip_processing = False
            
    except Exception as e:
        print(f"⚠️  Error loading existing index: {e}")
        if args.chat_only:
            sys.exit("❌  Cannot use chat-only mode: Failed to load existing index.")
        print("Creating new index...")
        # Create empty FAISS index using the proper method
        import faiss
        from langchain_community.docstore.in_memory import InMemoryDocstore
        
        # Get embedding dimensions by embedding a dummy text
        sample_embedding = emb.embed_query("hello")
        embedding_dim = len(sample_embedding)
        
        # Create empty FAISS index
        index = faiss.IndexFlatL2(embedding_dim)
        vectordb = FAISS(
            embedding_function=emb,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )
        skip_processing = False
else:
    if args.chat_only:
        sys.exit("❌  Cannot use chat-only mode: No existing FAISS index found.")
    
    # Create empty FAISS index using the proper method
    import faiss
    from langchain_community.docstore.in_memory import InMemoryDocstore
    
    # Get embedding dimensions by embedding a dummy text
    sample_embedding = emb.embed_query("hello")
    embedding_dim = len(sample_embedding)
    
    # Create empty FAISS index
    index = faiss.IndexFlatL2(embedding_dim)
    vectordb = FAISS(
        embedding_function=emb,
        index=index,
        docstore=InMemoryDocstore(),
        index_to_docstore_id={}
    )
    skip_processing = False

def page_to_text(page_id: str) -> str:
    """Flatten page blocks to plain text (no recursion into child pages)."""
    texts, cursor = [], None
    try:
        while True:
            resp = notion.blocks.children.list(
                block_id=page_id,
                start_cursor=cursor,
                page_size=100
            )
            for block in resp["results"]:
                tp = block["type"]
                if tp in ("paragraph", "heading_1", "heading_2",
                          "heading_3", "bulleted_list_item",
                          "numbered_list_item", "quote", "callout"):
                    if block[tp].get("rich_text"):
                        texts.extend([t["plain_text"] for t in block[tp]["rich_text"]])
            if not resp["has_more"]:
                break
            cursor = resp["next_cursor"]
    except Exception as e:
        print(f"Error extracting text from page {page_id}: {e}")
    
    return "\n".join(texts)

# Only process Notion pages if not skipping
if not skip_processing:
    print("🔍  Processing Notion pages...")
    new_chunks, new_meta = [], []
    processed_count = 0

    for top_page in iter_all_pages():
        try:
            txt = page_to_text(top_page["id"])
            if not txt.strip():
                continue
                
            chunks = splitter.split_text(txt)
            for c in chunks:
                new_chunks.append(c)
                new_meta.append({
                    "url": top_page.get("url", ""),
                    "page_id": top_page["id"]
                })
            
            processed_count += 1
            if processed_count % 10 == 0:
                print(f"Processed {processed_count} pages...")
                
        except Exception as e:
            print(f"Error processing page {top_page['id']}: {e}")
            continue

    if new_chunks:
        print(f"📝  Creating embeddings for {len(new_chunks)} chunks...")
        fresh = FAISS.from_texts(new_chunks, emb, metadatas=new_meta)
        
        if vectordb.index.ntotal > 0:
            vectordb.merge_from(fresh)
        else:
            vectordb = fresh
        
        vectordb.save_local(str(PERSIST_DIR))
        print(f"🔄  Added {len(new_chunks)} chunks; DB now has "
              f"{vectordb.index.ntotal} vectors.")
    else:
        print("✅  No new or edited pages to embed.")
else:
    print("⏭️  Skipping Notion processing - using existing cache.")

# ─── 3. INTERACTIVE RAG LOOP ────────────────────────────────────────
retriever = vectordb.as_retriever(
    search_type="mmr", 
    search_kwargs={"k": 4}
)

# Initialize the chat model once
chat = ChatOpenAI(model="gpt-3.5-turbo", openai_api_key=OPENAI_API_KEY)

HELP = "Type any question. Use 'exit' / 'quit' to leave.\n"

print("\n👉  Ready! " + HELP)
while True:
    try:
        q = input("You> ").strip()
    except (EOFError, KeyboardInterrupt):
        print("\nBye!")
        break
    
    if q.lower() in {"exit", "quit", ""}:
        break

    try:
        docs = retriever.invoke(q)
        context = "\n\n".join(d.page_content for d in docs)

        prompt = (f"Answer the question using ONLY the context below.\n"
                  f"Context:\n{context}\n\nQuestion: {q}")
        
        resp = chat.invoke(prompt).content
        print("\nAssistant:", resp, "\n")
        
    except Exception as e:
        print(f"Error processing query: {e}")
        continue