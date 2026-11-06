# Minecraft Resource Studio V2.0

A dark, Prism-inspired desktop resource-pack workspace for Minecraft Java Edition.

## Features
- Import Minecraft Java Edition client JAR files and browse their PNG textures.
- Import existing resource-pack ZIP files and PNG images.
- Search and browse texture assets.
- Inspect, replace, delete, and edit textures pixel by pixel.
- Create new textures and generate AI textures with a Gemini API key (model access required).
- Back up the workspace and export a resource-pack ZIP.
- Choose a Minecraft Java Edition version.
- Build a standalone Windows EXE with GitHub Actions.

## Build the Windows EXE
1. Open the repository's Actions tab.
2. Select Build Windows EXE.
3. Click Run workflow and wait for the workflow to complete.
4. Download the MinecraftResourcePackMaker-Windows artifact.

The EXE runs on Windows without requiring a separate Python installation.

## Run from source
```powershell
py -m pip install -r requirements.txt
py app.py
```

## Important notes
- To populate the library with the game's real textures, use Minecraft JAR 가져오기 and select the matching version's client JAR.
- Texture paths are retained inside the exported ZIP, so imported vanilla assets can be overridden by the resource pack.
- AI generation needs internet access and a Gemini API key with access to an image-generation model. Model availability and API behavior can change.
- This is a community utility and is not affiliated with or endorsed by Mojang or Microsoft.
