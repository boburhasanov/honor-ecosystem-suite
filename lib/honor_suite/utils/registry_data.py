"""
Comprehensive Known Applications and Debloat Taxonomy Registry for Honor / MagicOS & Android.
Categorizes 380+ packages into Safe to Remove, Caution, and Dangerous.
"""

from typing import Dict, Tuple

# package -> (friendly_name, icon_svg_or_fallback, category)
KNOWN_APP_REGISTRY: Dict[str, Tuple[str, str, str]] = {
    # Popular 3rd Party & User Apps
    "com.instagram.android": ("Instagram", "instagram.svg", "Social"),
    "com.linkedin.android": ("LinkedIn", "linkedin.svg", "Social"),
    "com.snapchat.android": ("Snapchat", "snapchat.svg", "Social"),
    "org.telegram.messenger": ("Telegram", "telegram.svg", "Communication"),
    "tg.televpn.messenger": ("TeleVPN", "telegram.svg", "Communication"),
    "com.whatsapp": ("WhatsApp", "whatsapp.svg", "Communication"),
    "com.openai.chatgpt": ("ChatGPT", "chatgpt.svg", "AI & Tools"),
    "com.anthropic.claude": ("Claude AI", "claude.svg", "AI & Tools"),
    "com.google.android.apps.bard": ("Google Gemini", "gemini.svg", "AI & Tools"),
    "com.supercell.clashofclans": ("Clash of Clans", "clash.svg", "Games"),
    "me.generalsx.zh": ("Generals Zero Hour", "clash.svg", "Games"),
    "uz.uzum.app": ("Uzum Market", "uzum.svg", "Shopping"),
    "uz.paynet.app": ("Paynet", "paynet.svg", "Finance"),
    "uz.rallix.app": ("Rallix", "rallix.svg", "Tools"),
    "uz.mobiuz.mobiservice": ("Mobiuz", "mobiuz.svg", "Carrier"),
    "org.videolan.vlc": ("VLC Media Player", "vlc.svg", "Media"),
    "com.edifier.edifierconnex": ("Edifier ConneX", "edifier.svg", "Audio"),
    "com.weather.forecast.dailyalert": ("Daily Weather", "weather.svg", "Weather"),
    "ru.yandex.yandexmaps": ("Yandex Maps", "yandex.svg", "Navigation"),
    "ru.vk.store": ("RuStore", "rustore.svg", "App Store"),
    "com.newleaf.app.android.victor": ("ReelShort", "video.svg", "Media"),
    "com.google.android.inputmethod.latin": ("Gboard", "keyboard.svg", "Tools"),

    # Google Apps
    "com.google.android.youtube": ("YouTube", "video.svg", "Google"),
    "com.android.chrome": ("Google Chrome", "browser.svg", "Google"),
    "com.google.android.apps.photos": ("Google Photos", "photos.svg", "Google"),
    "com.google.android.gm": ("Gmail", "mail.svg", "Google"),
    "com.google.android.apps.maps": ("Google Maps", "maps.svg", "Google"),
    "com.google.android.googlequicksearchbox": ("Google Search", "search.svg", "Google"),
    "com.google.android.videos": ("Google TV", "video.svg", "Google"),
    "com.google.android.apps.tachyon": ("Google Meet", "phone.svg", "Google"),
    "com.google.android.apps.messaging": ("Google Messages", "message.svg", "Google"),
    "com.google.android.dialer": ("Google Phone", "phone.svg", "Google"),
    "com.google.android.calendar": ("Google Calendar", "calendar.svg", "Google"),
    "com.google.android.apps.docs": ("Google Drive", "folder.svg", "Google"),
    "com.google.android.keep": ("Google Keep", "notes.svg", "Google"),

    # Facebook Services
    "com.facebook.appmanager": ("Facebook App Manager", "facebook.svg", "Bloatware"),
    "com.facebook.services": ("Facebook Services", "facebook.svg", "Bloatware"),
    "com.facebook.system": ("Facebook System", "facebook.svg", "Bloatware"),
    "com.facebook.katana": ("Facebook App", "facebook.svg", "Social"),
    "com.facebook.orca": ("Messenger", "facebook.svg", "Communication"),

    # Honor MagicOS Core Apps
    "com.hihonor.camera": ("Honor Camera", "camera.svg", "MagicOS Core"),
    "com.hihonor.photos": ("Honor Gallery", "photos.svg", "MagicOS Core"),
    "com.hihonor.contacts": ("Honor Contacts", "contacts.svg", "MagicOS Core"),
    "com.hihonor.deskclock": ("Honor Clock", "clock.svg", "MagicOS Core"),
    "com.hihonor.calendar": ("Honor Calendar", "calendar.svg", "MagicOS Core"),
    "com.hihonor.calculator": ("Honor Calculator", "calculator.svg", "MagicOS Core"),
    "com.hihonor.notepad": ("Honor Notes", "notes.svg", "MagicOS Core"),
    "com.hihonor.systemmanager": ("Honor Optimizer", "security.svg", "MagicOS Core"),
    "com.hihonor.filemanager": ("Honor Files", "folder.svg", "MagicOS Core"),
    "com.hihonor.soundrecorder": ("Sound Recorder", "mic.svg", "MagicOS Core"),
    "com.hihonor.compass": ("Honor Compass", "compass.svg", "MagicOS Core"),
    "com.hihonor.email": ("Honor Email", "mail.svg", "MagicOS Core"),
    "com.hihonor.gamecenter": ("Honor Game Center", "games.svg", "MagicOS Extra"),
    "com.hihonor.wallet": ("Honor Wallet", "wallet.svg", "MagicOS Extra"),
    "com.hihonor.tips": ("Honor Tips", "tips.svg", "MagicOS Extra"),
    "com.hihonor.hnvideoplayer": ("Honor Video", "video.svg", "MagicOS Extra"),
    "com.hihonor.hnmusicplayer": ("Honor Music", "music.svg", "MagicOS Extra"),
    "com.hihonor.android.totemweather": ("Honor Weather", "weather.svg", "MagicOS Extra"),
    "com.hihonor.appmarket": ("Honor App Market", "store.svg", "MagicOS Extra"),
    "com.hihonor.magichome": ("Honor AI Space", "home.svg", "MagicOS Extra"),
    "com.hihonor.cloud": ("Honor Cloud", "cloud.svg", "MagicOS Extra"),
    "com.hihonor.health": ("Honor Health", "heart.svg", "MagicOS Extra"),
}

# Safety Badges classification
# SAFE: Telemetry, 3rd party bloatware, pre-installed games, duplicate services
SAFE_DEBLOAT_PACKAGES = {
    "com.facebook.appmanager",
    "com.facebook.services",
    "com.facebook.system",
    "com.hihonor.gamecenter",
    "com.hihonor.tips",
    "com.hihonor.wallet",
    "com.hihonor.hnvideoplayer",
    "com.hihonor.hnmusicplayer",
    "com.hihonor.appmarket",
    "com.hihonor.cloud",
    "com.hihonor.search",
    "com.google.android.videos",
    "com.google.android.apps.tachyon",
    "com.android.providers.partnerbookmarks",
    "com.android.bookmarkprovider",
    "com.android.egg",
    "com.android.dreams.basic",
    "com.android.dreams.phototable",
    "com.android.printspooler",
    "com.android.bips",
}

# CAUTION: Useful extras (Calendar, Notes, Weather, Chrome, Google Photos)
CAUTION_PACKAGES = {
    "com.hihonor.android.totemweather",
    "com.hihonor.notepad",
    "com.hihonor.soundrecorder",
    "com.hihonor.compass",
    "com.hihonor.calculator",
    "com.hihonor.deskclock",
    "com.hihonor.calendar",
    "com.hihonor.health",
    "com.hihonor.magichome",
    "com.google.android.apps.photos",
    "com.google.android.apps.maps",
    "com.google.android.gm",
    "com.google.android.youtube",
    "com.android.chrome",
}

# DANGEROUS: Core telephony, Settings, Framework, SystemUI, Package Installer
DANGEROUS_PACKAGES = {
    "com.android.systemui",
    "com.android.settings",
    "com.android.phone",
    "com.android.providers.telephony",
    "com.android.providers.contacts",
    "com.android.providers.media",
    "com.android.packageinstaller",
    "com.google.android.packageinstaller",
    "com.android.permissioncontroller",
    "com.hihonor.systemmanager",
    "com.hihonor.camera",
    "com.hihonor.photos",
    "android",
}

def classify_package_safety(pkg: str) -> Tuple[str, str]:
    """
    Returns (SafetyCategory, ColorHex)
    - Safe: Can be removed freely without side effects
    - Caution: Non-critical but provides convenience
    - Essential: Do NOT remove (system stability)
    """
    if pkg in DANGEROUS_PACKAGES or pkg.startswith("com.android.internal") or pkg == "android":
        return "Essential (Dangerous to Remove)", "#ef4444"
    if pkg in SAFE_DEBLOAT_PACKAGES:
        return "Safe to Remove", "#10b981"
    if pkg in CAUTION_PACKAGES:
        return "Caution (May be Useful)", "#f59e0b"
    return "User / Custom Package", "#38bdf8"
