import sys
print(sys.executable)
try:
    import langchain
    import os
    print(f"LangChain file: {langchain.__file__}", flush=True)
    pkg_dir = os.path.dirname(langchain.__file__)
    print(f"Pkg dir: {pkg_dir}", flush=True)
    print(f"Dir contents: {os.listdir(pkg_dir)}", flush=True)

    import langchain.chains
    print("langchain.chains imported", flush=True)
except ImportError as e:
    print(f"Import failed: {e}", flush=True)
except Exception as e:
    print(f"Error: {e}")
