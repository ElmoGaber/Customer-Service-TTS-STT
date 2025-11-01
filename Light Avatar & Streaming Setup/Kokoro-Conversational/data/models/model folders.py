import os
import requests
import logging
import zipfile
from pathlib import Path

# ----------------- إعداد الـ Logger -----------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("model_download.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ----------------- إعداد المسارات -----------------
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models_downloaded"
MODELS_DIR.mkdir(exist_ok=True)

# ----------------- دالة تحميل الموديل من GitHub -----------------
def download_model(repo_url: str, output_dir: Path):
    """
    تحميل موديل من GitHub كمجلد أو ملف zip.
    """
    try:
        repo_name = repo_url.split("/")[-1].replace(".git", "")
        model_path = output_dir / repo_name

        if model_path.exists():
            logger.info(f"المجلد {repo_name} موجود بالفعل، سيتم تخطي التحميل.")
            return model_path

        zip_url = repo_url.replace(".git", "") + "/archive/refs/heads/main.zip"
        zip_path = output_dir / f"{repo_name}.zip"

        logger.info(f"جارٍ تحميل الموديل من: {zip_url}")
        response = requests.get(zip_url, stream=True)
        response.raise_for_status()

        with open(zip_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        logger.info(f"تم تحميل {repo_name} بنجاح ✅")

        # فك الضغط
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(output_dir)
        logger.info(f"تم فك ضغط {repo_name}")

        # حذف ملف الـ ZIP بعد فك الضغط
        os.remove(zip_path)
        logger.info(f"تم حذف ملف zip المؤقت لـ {repo_name}")

        return model_path
    except Exception as e:
        logger.error(f"خطأ أثناء تحميل الموديل من {repo_url}: {e}")
        return None

# ----------------- دالة لضغط المجلد -----------------
def compress_folder(folder_path: Path, output_zip: Path):
    """
    ضغط مجلد إلى ملف zip.
    """
    try:
        logger.info(f"جارٍ ضغط المجلد: {folder_path.name}")
        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(folder_path):
                for file in files:
                    abs_path = Path(root) / file
                    rel_path = abs_path.relative_to(folder_path.parent)
                    zipf.write(abs_path, rel_path)
        logger.info(f"تم إنشاء الملف المضغوط: {output_zip}")
    except Exception as e:
        logger.error(f"خطأ أثناء ضغط المجلد {folder_path}: {e}")

# ----------------- دالة رئيسية -----------------
def main():
    # روابط الموديلات اللي هتنزلها من GitHub
    model_repos = [
        "https://github.com/maitrix-org/Voila-chat.git",
        "https://github.com/tencent/SongPrep-7B.git",
        "https://github.com/Kamtera/persian-tts-female-vits.git"
    ]

    logger.info("🚀 بدء تحميل الموديلات...")
    for repo in model_repos:
        model_path = download_model(repo, MODELS_DIR)
        if model_path:
            zip_output = MODELS_DIR / f"{model_path.name}.zip"
            compress_folder(model_path, zip_output)

    logger.info("✅ اكتمل التحميل والضغط. الموديلات جاهزة للرفع على GitHub يدوياً.")

# ----------------- تشغيل البرنامج -----------------
if __name__ == "__main__":
    main()
