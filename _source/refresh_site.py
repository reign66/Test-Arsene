import subprocess
import os
import sys

def run_script(script_name):
    print(f"🚀 Running {script_name}...")
    try:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(BASE_DIR, script_name)
        # Use sys.executable to ensure we use the same python interpreter
        result = subprocess.run([sys.executable, script_path], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {script_name} finished successfully.")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"❌ Error in {script_name}:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Exception running {script_name}: {e}")
        return False
    return True

if __name__ == "__main__":
    if run_script("generate.py"):
        run_script("generate_departements.py")
        run_script("generate_sitemap.py")
        print("🏁 Full site refresh complete.")
    else:
        print("❌ Site generation failed.")
