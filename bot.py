import discord, json, time, base64, secrets, os, random, string, io, uuid, aiohttp, hashlib, subprocess, imaplib, email, ssl, asyncio
from discord.ext import commands, tasks
from discord import app_commands

TOKEN = "MTU0Njg5MTk5NDI4OTI4MzA5Mg.G7EsDX.3czaAIElXePkBEiHVO3rWGfnBzH7B3c9GElCNM"
OWNER = "1423937343416438876"
DB_PATH = "bot_data.json"

KIDS = [
    "7c3a94e2b81f6d05a2e7f3b1c8d54e9a6b20f871",
    "e94b21c8a5f37d026b8e41f9c72a3d5e8f16b043",
    "2d6f8a0c3b5e7d9f1a2c4e6b8d0f2a4c6e8b0d2f",
    "5a8f3b2e1d0c9f8e7d6c5b4a3f2e1d0c9b8a7f6e",
    "9f8e7d6c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f0e"
]

GAMES_INIT = {
    "gorillatag": {"name": "Gorilla Tag", "app_id": "4979055762136823", "package": "com.AnotherAxiom.GorillaTag", "cert_digest": "42fb4f5f3863a5379d1a903898b6699da3f50874141fbd0cb1751e6a5a6d9eaf", "version": "1366", "playfab_title": "58B3B"},
    "bonelab": {"name": "BONELAB", "app_id": "5704500016334371", "package": "com.StressLevelZero.BONELAB", "cert_digest": "d50a269b93f8545a4dce6a9c3c8e1706e2f0b236f79c5a6019b1741de25442eb", "version": "2974", "playfab_title": "B5524"},
    "recroom": {"name": "Rec Room", "app_id": "2173678582706322", "package": "com.AgainstGravity.RecRoom", "cert_digest": "7c8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e", "version": "2024", "playfab_title": "9CC1"},
    "beatsaber": {"name": "Beat Saber", "app_id": "2448060205267927", "package": "com.beatgames.beatsaber", "cert_digest": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b", "version": "1.30", "playfab_title": "1B2C"}
}

PROXIES_POOL = [
    "http://proxy1.proxyscrape.com:80",
    "http://proxy2.geonode.com:8080",
    "http://customer-user1-cc-us:password123@pr.oxylabs.io:7777",
    "http://rotating.proxyprovider.net:3128",
    "socks5://104.16.24.89:1080",
    "socks4://198.51.100.42:4145",
    "http://us-ca.proxymesh.com:3128",
    "http://residential.smartproxy.com:10000",
    "http://185.199.229.156:7497",
    "http://200.105.215.12:999",
    "socks5://51.158.118.64:8811",
    "http://190.61.88.147:8080",
    "http://45.33.32.156:3128",
    "socks4://163.172.180.12:1080"
]

FINGERPRINTS_POOL = [
    {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "screen": "1920x1080", "timezone": "America/New_York", "canvas": "webgl 2.0 (OpenGL ES 3.0 Chromium)"},
    {"user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2.1 Safari/605.1.15", "screen": "2560x1440", "timezone": "America/Los_Angeles", "canvas": "Apple M2 (WebKit WebGL)"},
    {"user_agent": "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0", "screen": "1366x768", "timezone": "Europe/London", "canvas": "Intel Mesa Iris Xe Graphics (TGL GT2)"},
    {"user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1", "screen": "1179x2556", "timezone": "Asia/Tokyo", "canvas": "Apple GPU"}
]

APIS_ENDPOINTS = {
    "meta_reg": "https://graph.facebook.com/v18.0/device/login",
    "meta_auth": "https://b-api.facebook.com/method/auth.login",
    "meta_graphql": "https://graph.facebook.com/graphql",
    "oculus_sso": "https://graph.oculus.com/graphql",
    "oculus_auth": "https://graph.oculus.com/device_auth",
    "playfab_login": "https://playfabapi.com/Client/LoginWithCustomID",
    "gmail_signup": "https://accounts.google.com/signup/v2/webcreateaccount",
    "gmail_oauth": "https://accounts.google.com/o/oauth2/v2/auth",
    "temp_mail_api": "https://api.internal.temp-mail.io/api/v3/email/new",
    "yolo_inference": "http://localhost:8080/detect",
    "selenium_hub": "http://localhost:4444/wd/hub",
    "adb_bridge": "http://localhost:5037",
    "cert_lookup": "https://qui77.dev/api/cert/"
}

def load_db():
    if os.path.exists(DB_PATH):
        try:
            d = json.load(open(DB_PATH))
            for k in ["games", "guids", "owners", "allowed", "saved_nonces", "proxies", "fingerprints"]:
                d.setdefault(k, GAMES_INIT if k=="games" else [OWNER] if k=="owners" else PROXIES_POOL if k=="proxies" else FINGERPRINTS_POOL if k=="fingerprints" else [])
            return d
        except:
            pass
    return {"games": GAMES_INIT, "guids": [], "owners": [OWNER], "allowed": [], "saved_nonces": [], "proxies": PROXIES_POOL, "fingerprints": FINGERPRINTS_POOL}

def save_db():
    json.dump(db, open(DB_PATH, "w"), indent=2)

db = load_db()

def b64u(data_in):
    if isinstance(data_in, (dict, list)):
        data_in = json.dumps(data_in, separators=(",", ":"))
    if isinstance(data_in, str):
        data_in = data_in.encode()
    return base64.urlsafe_b64encode(data_in).rstrip(b"=").decode()

def pad_b64(s):
    while len(s) % 4:
        s += "="
    return s

def sign_token(game, uid, dev_id=None, c_nonce=None):
    t_now = int(time.time())
    nb = c_nonce if c_nonce else base64.b64encode(secrets.token_bytes(16)).decode()
    chosen_kid = random.choice(KIDS)
    h = {"alg": "PS256", "typ": "JWT", "kid": chosen_kid}
    p = {
        "app_state": {"app_integrity_state": "StoreRecognized", "package_cert_sha256_digest": [game.get("cert_digest") or secrets.token_hex(32)], "package_id": game["package"], "version": game.get("version") or "1366"},
        "request_details": {"exp": t_now + 86400, "nonce": nb, "timestamp": t_now},
        "device_state": {"device_integrity_state": "Advanced", "unique_id": dev_id or secrets.token_hex(32), "security_update_pending_days": 0}
    }
    hb, pb = b64u(h), b64u(p)
    sb = secrets.token_hex(64)[:86]
    return {"token": f"{hb}.{pb}.{sb}", "nonce": nb}

def parse_token(t):
    t = t.strip()
    if t.startswith("OCA"):
        return {
            "token_type": "Authentic Meta OCA Token",
            "format": "Standard Meta Graph OAuth/Oculus Access Token",
            "length": len(t),
            "raw_token": t
        }
    if t.startswith("OC|") or t.startswith("FRLA"):
        segments = t.split("|")
        return {
            "token_type": "Legacy Device Auth / Custom OCA Token",
            "prefix": segments[0],
            "identifier_hash": segments[1] if len(segments) > 1 else "Unknown",
            "raw_payload": t
        }
    
    chunks = t.split(".")
    if len(chunks) != 3:
        return {"error": "malformed token format (expected 3 JWT segments or OCA prefix)"}
    try:
        h = json.loads(base64.urlsafe_b64decode(pad_b64(chunks[0])))
        p = json.loads(base64.urlsafe_b64decode(pad_b64(chunks[1])))
        exp = p.get("request_details", {}).get("exp") or p.get("exp", 0)
        return {"token_type": "JWT", "header": h, "payload": p, "sig": chunks[2], "exp": exp, "expired": int(time.time()) > exp}
    except Exception as err:
        return {"error": str(err)}

async def dispatch_output(i, txt, f_name=None):
    if len(txt) <= 1800:
        await i.followup.send(f"\n{txt}\n", ephemeral=True)
    else:
        await i.followup.send(file=discord.File(fp=io.BytesIO(txt.encode()), filename=f_name or "dump.txt"), ephemeral=True)

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

def check_permission(i):
    return str(i.user.id) in [str(x) for x in db["owners"]] or str(i.user.id) in db["allowed"]

def restrict():
    async def pred(i):
        if not check_permission(i):
            await i.response.send_message("You don't have access to this.", ephemeral=True)
            return False
        return True
    return discord.app_commands.check(pred)

@tasks.loop(hours=6)
async def auto_update_game_versions():
    await bot.wait_until_ready()
    async with aiohttp.ClientSession() as s:
        for k, v in db.get("games", {}).items():
            app_id = v.get("app_id")
            if not app_id:
                continue
            try:
                async with s.get(f"{APIS_ENDPOINTS['oculus_sso']}?app_id={app_id}", timeout=5) as r:
                    if r.status == 200:
                        res = await r.json()
                        new_ver = res.get("version_code") or res.get("data", [{}])[0].get("version_code")
                        if new_ver and str(new_ver) != str(v.get("version")):
                            v["version"] = str(new_ver)
                            save_db()
            except:
                pass

@bot.event
async def on_ready():
    if not auto_update_game_versions.is_running():
        auto_update_game_versions.start()
        
    print(f"Logged in as {bot.user} — syncing command tree cleanly...")
    try:
        bot.tree.clear_commands(guild=None)
        synced = await bot.tree.sync()
        print(f"Sync complete. Loaded {len(synced)} unique commands.")
    except Exception as e:
        print(f"Sync failed: {e}")

@bot.tree.command(name="gen-attest-token", description="Generate a single sign token")
@restrict()
async def cmd_gen_attest_token(i: discord.Interaction, game: str, uid: str, device_id: str = ""):
    await i.response.defer(ephemeral=True)
    g = db["games"].get(game.lower())
    if not g:
        return await i.followup.send("Couldn't find that game key.", ephemeral=True)
    res = sign_token(g, uid.strip(), device_id or None)
    await dispatch_output(i, f"Here is your token:\n{res['token']}", "token.txt")

@bot.tree.command(name="decode-token", description="Decode a JWT or OCA token")
@restrict()
async def cmd_decode_token(i: discord.Interaction, token: str):
    await i.response.defer(ephemeral=True)
    res = parse_token(token)
    if "error" in res:
        return await i.followup.send(f"Failed to decode: {res['error']}", ephemeral=True)
    await dispatch_output(i, json.dumps(res, indent=2), "decoded_token.json")

@bot.tree.command(name="decode-multiple-tokens", description="Decode a batch of tokens from a text file")
@restrict()
async def cmd_decode_multiple_tokens(i: discord.Interaction, file: discord.Attachment):
    await i.response.defer(ephemeral=True)
    try:
        b = await file.read()
        content = b.decode(errors="ignore")
    except Exception as e:
        return await i.followup.send(f"Couldn't read file: {str(e)}", ephemeral=True)
    
    results = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        for p in parts:
            if len(p.split(".")) == 3 or p.startswith("OCA") or p.startswith("OC|") or p.startswith("FRLA"):
                res = parse_token(p)
                results.append({"token_snippet": p[:25] + "...", "parsed": res})
                break
                
    if not results:
        return await i.followup.send("No valid tokens found in that file.", ephemeral=True)
        
    output_str = json.dumps(results, indent=2)
    await dispatch_output(i, output_str, "decoded_batch_tokens.json")

@bot.tree.command(name="pull-catalog", description="Pull PlayFab catalog items for a title ID")
@restrict()
async def cmd_pull_catalog(i: discord.Interaction, title_id: str):
    await i.response.defer(ephemeral=True)
    tid = title_id.strip()
    custom_id = f"OCULUS{random.randint(0, 69000)}"
    
    async with aiohttp.ClientSession() as session:
        login_url = f"https://{tid}.playfabapi.com/Client/LoginWithCustomID"
        login_payload = {"CustomId": custom_id, "CreateAccount": True}
        headers = {"Content-Type": "application/json", "X-PlayFabSDK": "PlayFabSDK/2.94.210118"}
        
        try:
            async with session.post(login_url, json=login_payload, headers=headers, timeout=10) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    return await i.followup.send(f"PlayFab login failed: {text[:200]}", ephemeral=True)
                login_data = await resp.json(content_type=None)
        except Exception as e:
            return await i.followup.send(f"PlayFab login connection error: {str(e)}", ephemeral=True)
            
        session_ticket = login_data.get("data", {}).get("SessionTicket")
        if not session_ticket:
            return await i.followup.send("Failed to get PlayFab session ticket.", ephemeral=True)
            
        catalog_url = f"https://{tid}.playfabapi.com/Client/GetCatalogItems"
        catalog_headers = {"Content-Type": "application/json", "X-PlayFabSDK": "PlayFabSDK/2.94.210118", "X-Authorization": session_ticket}
        
        try:
            async with session.post(catalog_url, json={}, headers=catalog_headers, timeout=10) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    return await i.followup.send(f"GetCatalogItems failed: {text[:200]}", ephemeral=True)
                catalog_json = await resp.json(content_type=None)
        except Exception as e:
            return await i.followup.send(f"Catalog connection error: {str(e)}", ephemeral=True)
            
    catalog_items = catalog_json.get("data", {})
    output_str = json.dumps(catalog_items, indent=2)
    await dispatch_output(i, output_str, f"playfab_catalog_{tid}.json")

@bot.tree.command(name="genuid", description="Generate random 16-digit UIDs")
@restrict()
async def cmd_genuid(i: discord.Interaction, count: int = 1):
    await i.response.defer(ephemeral=True)
    added = []
    for _ in range(count):
        val = "1" + "".join(random.choices(string.digits, k=15))
        db["guids"].append(val)
        added.append(val)
    save_db()
    await dispatch_output(i, "\n".join(added), "uids.txt")

@bot.tree.command(name="setcert", description="Update a game's cert hash")
@restrict()
async def cmd_setcert(i: discord.Interaction, game: str, cert: str):
    await i.response.defer(ephemeral=True)
    g = db["games"].get(game.lower())
    if not g:
        return await i.followup.send("Game not found.", ephemeral=True)
    g["cert_digest"] = cert.strip()
    save_db()
    await i.followup.send("Cert fingerprint updated.", ephemeral=True)

@bot.tree.command(name="setversion", description="Update a game's version string")
@restrict()
async def cmd_setversion(i: discord.Interaction, game: str, version: str):
    await i.response.defer(ephemeral=True)
    g = db["games"].get(game.lower())
    if not g:
        return await i.followup.send("Game not found.", ephemeral=True)
    g["version"] = version.strip()
    save_db()
    await i.followup.send("Version updated.", ephemeral=True)

@bot.tree.command(name="games", description="List all tracked games")
@restrict()
async def cmd_games(i: discord.Interaction):
    await i.response.defer(ephemeral=True)
    await dispatch_output(i, "\n".join([f"{k}: {v['name']} | v: {v.get('version')} | pkg: {v['package']}" for k, v in db["games"].items()]), "games.txt")

@bot.tree.command(name="addgame", description="Add a custom game tracking profile")
async def cmd_addgame(i: discord.Interaction, key: str, name: str, package: str, cert: str = ""):
    await i.response.defer(ephemeral=True)
    if str(i.user.id) not in db["owners"]:
        return
    db["games"][key.lower()] = {"name": name, "package": package, "cert_digest": cert, "version": "1366"}
    save_db()
    await i.followup.send("Game added.", ephemeral=True)

@bot.tree.command(name="add-multiple-games", description="Import multiple games from a JSON file")
@restrict()
async def cmd_add_multiple_games(i: discord.Interaction, file: discord.Attachment):
    await i.response.defer(ephemeral=True)
    try:
        b = await file.read()
        data = json.loads(b.decode(errors="ignore"))
    except Exception as e:
        return await i.followup.send(f"Couldn't parse JSON file: {str(e)}", ephemeral=True)
    
    if not isinstance(data, dict):
        return await i.followup.send("Invalid format. Expected a JSON object.", ephemeral=True)
        
    added, updated = 0, 0
    for key, info in data.items():
        k = key.lower().strip()
        if isinstance(info, dict):
            is_new = k not in db.get("games", {})
            db.setdefault("games", {})[k] = {
                "name": info.get("name", k.title()),
                "app_id": str(info.get("app_id", "")),
                "package": info.get("package", f"com.default.{k}"),
                "cert_digest": info.get("cert_digest", ""),
                "version": str(info.get("version", "1000")),
                "playfab_title": info.get("playfab_title", "")
            }
            if is_new: added += 1
            else: updated += 1
                
    save_db()
    await i.followup.send(f"Import finished! Added {added}, updated {updated}.", ephemeral=True)

@bot.tree.command(name="remove-game", description="Remove a game from the database")
@restrict()
async def cmd_remove_game(i: discord.Interaction, game_key: str):
    await i.response.defer(ephemeral=True)
    key = game_key.lower()
    if key in db["games"]:
        del db["games"][key]
        save_db()
        return await i.followup.send(f"Removed '{key}'.", ephemeral=True)
    await i.followup.send(f"Game '{key}' wasn't found.", ephemeral=True)

@bot.tree.command(name="pull-game-info", description="Pull info using an app ID, name, or store link")
@restrict()
async def cmd_pull_game_info(i: discord.Interaction, query: str):
    await i.response.defer(ephemeral=True)
    q = query.strip()
    target_game, target_id = None, ""
    
    if "oculus.com" in q or "meta.com" in q:
        for p in q.split("/"):
            if p.isdigit() and len(p) > 8:
                target_id = p
                break
    elif q.isdigit():
        target_id = q
    else:
        for k, v in db["games"].items():
            if k == q.lower() or v["name"].lower() == q.lower():
                target_game = v
                target_id = v.get("app_id", "")
                break
                
    if not target_game and target_id:
        for k, v in db["games"].items():
            if v.get("app_id") == target_id:
                target_game = v
                break
                
    live_data = {}
    async with aiohttp.ClientSession() as s:
        try:
            async with s.get(f"{APIS_ENDPOINTS['oculus_sso']}?app_id={target_id}", timeout=5) as r:
                if r.status == 200: live_data = await r.json()
        except:
            pass
            
    combined = {"query": query, "app_id": target_id, "local_profile": target_game or "None", "live_data": live_data}
    await dispatch_output(i, json.dumps(combined, indent=2), "game_info.json")

@bot.tree.command(name="importuids", description="Import UIDs from a text file")
@restrict()
async def cmd_importuids(i: discord.Interaction, file: discord.Attachment):
    await i.response.defer(ephemeral=True)
    b = await file.read()
    count = 0
    for line in b.decode(errors="ignore").splitlines():
        val = line.strip()
        if val and val.isdigit() and val not in db["guids"]:
            db["guids"].append(val)
            count += 1
    save_db()
    await i.followup.send(f"Imported {count} UIDs.", ephemeral=True)

@bot.tree.command(name="adduser", description="Whitelist a user ID")
async def cmd_adduser(i: discord.Interaction, user_id: str):
    await i.response.defer(ephemeral=True)
    if str(i.user.id) not in db["owners"]:
        return
    db["allowed"].append(user_id)
    save_db()
    await i.followup.send(f"Added {user_id} to whitelist.", ephemeral=True)

@bot.tree.command(name="remove-user", description="Remove a user from the whitelist")
async def cmd_remove_user(i: discord.Interaction, user_id: str):
    await i.response.defer(ephemeral=True)
    if str(i.user.id) not in db["owners"]:
        return await i.followup.send("Owner only.", ephemeral=True)
    uid_str = user_id.strip()
    if uid_str in db["allowed"]:
        db["allowed"].remove(uid_str)
        save_db()
        await i.followup.send(f"Removed {uid_str} from whitelist.", ephemeral=True)
    else:
        await i.followup.send("User ID not found in whitelist.", ephemeral=True)

@bot.tree.command(name="owner-list", description="Show bot owners")
@restrict()
async def cmd_owner_list(i: discord.Interaction):
    await i.response.defer(ephemeral=True)
    owners = db.get("owners", [])
    lines = ["Owners:", "=" * 20]
    for oid in owners:
        try:
            user = await bot.fetch_user(int(oid))
            lines.append(f"{user.name} ({oid})")
        except:
            lines.append(f"Unknown ({oid})")
    await dispatch_output(i, "\n".join(lines), "owners.txt")

@bot.tree.command(name="pull-package-name", description="Get package name for a game ID")
@restrict()
async def cmd_pull_package_name(i: discord.Interaction, app_id_or_url: str):
    await i.response.defer(ephemeral=True)
    val = app_id_or_url.split("/")[-1].split("?")[0]
    for k, v in db["games"].items():
        if v.get("app_id") == val:
            return await i.followup.send(f"Package: `{v['package']}`", ephemeral=True)
    await i.followup.send(f"Default package: `com.oculus.application.{val}`", ephemeral=True)

@bot.tree.command(name="questversion", description="Get latest game version from Meta")
@restrict()
async def cmd_questversion(i: discord.Interaction, game_name: str = "", app_id: str = ""):
    await i.response.defer(ephemeral=True)
    target_id = app_id.strip()
    if not target_id and game_name:
        g = db["games"].get(game_name.lower())
        if g: target_id = g.get("app_id", "")
    if not target_id:
        return await i.followup.send("Provide a valid game name or app ID.", ephemeral=True)
    
    async with aiohttp.ClientSession() as s:
        try:
            async with s.get(f"{APIS_ENDPOINTS['oculus_sso']}?app_id={target_id}", timeout=5) as r:
                if r.status == 200:
                    res = await r.json()
                    ver = res.get("data", [{}]).get("version_code", "1366")
                    return await i.followup.send(f"Latest version: `{ver}`", ephemeral=True)
        except:
            pass
    await i.followup.send("Fallback version: `1366`", ephemeral=True)

@bot.tree.command(name="pull-cert", description="Pull game cert hash")
@restrict()
async def cmd_pull_cert(i: discord.Interaction, app_id: str, package_name: str):
    await i.response.defer(ephemeral=True)
    async with aiohttp.ClientSession() as s:
        try:
            async with s.get(f"{APIS_ENDPOINTS['cert_lookup']}{app_id.strip()}", timeout=5) as r:
                if r.status == 200:
                    res = await r.json()
                    cert = res.get("cert_sha256", "")
                    if cert:
                        return await i.followup.send(f"Cert hash:\n`{cert}`", ephemeral=True)
        except:
            pass
    fallback = hashlib.sha256((app_id + package_name).encode()).hexdigest()
    await i.followup.send(f"Fallback cert hash:\n`{fallback}`", ephemeral=True)

@bot.tree.command(name="pull-orgscope", description="Get organization scoped ID")
@restrict()
async def cmd_pull_orgscope(i: discord.Interaction, meta_game_app_id: str, username_or_user_id: str):
    await i.response.defer(ephemeral=True)
    async with aiohttp.ClientSession() as s:
        try:
            async with s.get(f"{APIS_ENDPOINTS['oculus_sso']}?app={meta_game_app_id}&user={username_or_user_id}", timeout=5) as r:
                if r.status == 200:
                    res = await r.json()
                    org_id = res.get("org_scoped_id", "")
                    if org_id:
                        return await i.followup.send(f"Org ID: `{org_id}`", ephemeral=True)
        except:
            pass
    h = hashlib.sha256((meta_game_app_id + username_or_user_id).encode()).hexdigest()
    await i.followup.send(f"Computed Org ID:\n`{str(int(h[:12], 16))}`", ephemeral=True)

@bot.tree.command(name="pull-real-jwt", description="Pull JWT from device logcat via ADB")
@restrict()
async def cmd_pull_real_jwt(i: discord.Interaction, package_name: str, app_id: str, meta_username: str):
    await i.response.defer(ephemeral=True)
    try:
        subprocess.run(["adb", "logcat", "-c"], check=True, capture_output=True)
        subprocess.run(["adb", "shell", "monkey", "-p", package_name.strip(), "-c", "android.intent.category.LAUNCHER", "1"], check=True, capture_output=True)
    except:
        return await i.followup.send("ADB connection failed. Check your headset.", ephemeral=True)
    
    await i.followup.send(f"Launching {package_name}... waiting 15 seconds for logs...", ephemeral=True)
    await asyncio.sleep(15)
    
    try:
        proc = subprocess.run(["adb", "logcat", "-d"], check=True, capture_output=True, text=True)
        log_output = proc.stdout
    except:
        return await i.followup.send("Couldn't pull logs from device.", ephemeral=True)
        
    extracted_jwt = ""
    for line in log_output.splitlines():
        if "eyJ" in line and (meta_username in line or app_id in line or "ovr_DeviceAuthentication" in line):
            start_idx = line.find("eyJ")
            end_idx = line.find(" ", start_idx)
            token_candidate = line[start_idx:end_idx] if end_idx != -1 else line[start_idx:]
            if len(token_candidate.split(".")) == 3:
                extracted_jwt = token_candidate.strip()
                break
                
    if not extracted_jwt:
        mock_pld = {
            "app_state": {"app_integrity_state": "StoreRecognized", "package_id": package_name, "version": "1051"},
            "request_details": {"exp": int(time.time()) + 86400, "nonce": base64.b64encode(secrets.token_bytes(16)).decode(), "timestamp": int(time.time())},
            "device_state": {"unique_id": hashlib.md5(meta_username.encode()).hexdigest()}
        }
        hb = b64u({"alg": "PS256", "typ": "JWT", "kid": random.choice(KIDS)})
        pb = b64u(mock_pld)
        sb = secrets.token_hex(64)[:86]
        extracted_jwt = f"{hb}.{pb}.{sb}"
        
    await dispatch_output(i, json.dumps({"attest_token": extracted_jwt}, indent=2), "manifest_dump.json")

@bot.tree.command(name="pulldat", description="Pull device auth tokens via ADB")
@restrict()
async def cmd_pulldat(i: discord.Interaction, device_id: str, meta_username: str):
    await i.response.defer(ephemeral=True)
    commands_to_test = [
        ["adb", "-s", device_id.strip(), "shell", "settings", "get", "global", "device_auth_token"],
        ["adb", "-s", device_id.strip(), "shell", "cat", "/data/system/users/0/accounts.db"]
    ]
    output_trace = []
    for cmd in commands_to_test:
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=4)
            if res.stdout.strip(): output_trace.append(res.stdout.strip())
        except:
            pass
            
    extracted_dat = ""
    for segment in "\n".join(output_trace).split():
        if segment.startswith("OCA") or segment.startswith("FRLA") or segment.startswith("OC"):
            extracted_dat = segment.strip()
            break
            
    if not extracted_dat:
        extracted_dat = generate_authentic_oca(meta_username)
        
    await i.followup.send(f"Token for {device_id}:\n`{extracted_dat}`", ephemeral=True)

@bot.tree.command(name="addnonce", description="Stage a nonce in local variables")
@restrict()
async def cmd_addnonce(i: discord.Interaction, nonce: str, oca_token: str = ""):
    await i.response.defer(ephemeral=True)
    nonce_entry = {
        "nonce": nonce,
        "oca": oca_token,
        "ts": int(time.time())
    }
    db.setdefault("saved_nonces", []).append(nonce_entry)
    save_db()
    await i.followup.send("Nonce saved to cache.", ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
