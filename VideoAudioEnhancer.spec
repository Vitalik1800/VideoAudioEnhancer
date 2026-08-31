from pathlib import Path

from PyInstaller.utils.hooks import collect_all


project_root = Path.cwd()


datas = [
    (
        str(
            project_root
            / "ai_models"
            / "audio_gain_model.pth"
        ),
        "ai_models"
    ),
]


binaries = []

hiddenimports = [
    "soundfile"
]


for package in [
    "customtkinter",
    "torch",
    "torchaudio",
    "librosa",
    "cv2",
]:
    try:
        package_datas, package_binaries, package_hiddenimports = (
            collect_all(package)
        )

        datas.extend(package_datas)
        binaries.extend(package_binaries)
        hiddenimports.extend(package_hiddenimports)

    except Exception:
        pass


a = Analysis(
    ["main.py"],
    pathex=[
        str(project_root)
    ],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)


pyz = PYZ(
    a.pure
)


exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="VideoAudioEnhancerAI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon=str(
        project_root
        / "assets"
        / "icon.ico"
    )
)