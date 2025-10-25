import os
from django.core.management.base import BaseCommand
from myproject import settings
import pytesseract
from PIL import Image


OUTPUT_FILE = os.path.join(settings.BASE_DIR, "extracted_reviews.html")

class Command(BaseCommand):
    help = "OCR PNG feedback images and produce HTML review snippets"

    def handle(self, *args, **options):
        if pytesseract is None:
            self.stderr.write("pytesseract not installed.")
            return
        img_dir_candidates = [
            os.path.join(settings.BASE_DIR, "static", "assets", "images", "feedback"),
            os.path.join(settings.BASE_DIR, "staticfiles", "assets", "images", "feedback"),
        ]
        img_dir = next((c for c in img_dir_candidates if os.path.isdir(c)), None)
        if not img_dir:
            self.stderr.write("feedback images directory not found.")
            return

        cards = []
        for name in sorted(os.listdir(img_dir)):
            if not name.lower().endswith(".png"):
                continue
            path = os.path.join(img_dir, name)
            try:
                text = pytesseract.image_to_string(Image.open(path)).strip()
                if not text:
                    continue
                safe_text = "\n".join(line.strip() for line in text.splitlines() if line.strip())
                card_html = f"""
<div class="card mb-3 review-item">
  <div class="d-flex flex-column align-items-center mb-3">
    <span class="rounded-circle bg-secondary d-flex justify-content-center align-items-center"
          style="width:70px; height:70px;">
      <i class="fa fa-user fa-2x text-white"></i>
    </span>
    <h5 class="card-title">{name}</h5>
    <div class="mt-2">
      <span class="text-warning"><i class="fa fa-star"></i></span>
      <span class="text-warning"><i class="fa fa-star"></i></span>
      <span class="text-warning"><i class="fa fa-star"></i></span>
      <span class="text-warning"><i class="fa fa-star"></i></span>
      <span class="text-warning"><i class="fa fa-star"></i></span>
    </div>
  </div>
  <p class="card-text" style="white-space:pre-line;">{safe_text}</p>
  <p class="card-text"><small class="text-muted">Дата: --.--.----</small></p>
</div>
"""
                cards.append(card_html)
                self.stdout.write(f"Processed {name}")
            except Exception as e:
                self.stderr.write(f"Failed {name}: {e}")

        if not cards:
            self.stderr.write("No text extracted.")
            return

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write("<!-- OCR Generated Review Cards -->\n")
            for c in cards:
                f.write(c + "\n")

        self.stdout.write(f"Saved HTML snippets to {OUTPUT_FILE}")