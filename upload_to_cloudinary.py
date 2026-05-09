import cloudinary
import cloudinary.uploader
import os

cloudinary.config(
    cloud_name="dtr8o0saj",
    api_key="528619111547163",
    api_secret="mcoA3xpg68jGDYHPavzRSgw69-I",
    secure=True
)

# Dossier contenant tes images (toute la hiérarchie)
media_folder = "D:/AJGL/media"

# Parcourir tous les sous-dossiers
for root, dirs, files in os.walk(media_folder):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            file_path = os.path.join(root, file)
            # Garder la structure des dossiers (ex: slider/slide1.jpg)
            relative_path = os.path.relpath(file_path, media_folder)
            folder_name = os.path.dirname(relative_path).replace("\\", "/")
            
            # Upload vers Cloudinary
            result = cloudinary.uploader.upload(
                file_path,
                folder=f"ajgl/{folder_name}" if folder_name != "." else "ajgl",
                use_filename=True,
                unique_filename=False
            )
            print(f"✅ Uploadé : {relative_path} → {result['secure_url']}")

print("\n🎉 Toutes les images ont été uploadées wesh kbf !")