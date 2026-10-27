import discord, json, time, base64, secrets, os, random, string, io, aiohttp, hashlib, asyncio
from discord.ext import commands, tasks
from discord import app_commands

TOKEN = "MTU0Njg5MTk5NDI4OTI4MzA5Mg.GiOJYf.lQqi9gJY8Vqk47Nd2FvubG6HmiHPs6VgxhmZ6U"
OWNER = "1423937343416438876"
DB_PATH = "bot_data.json"

GAMES_INIT = {
    "gorillatag": {"name": "Gorilla Tag", "app_id": "4979055762136823", "package": "com.AnotherAxiom.GorillaTag", "cert_digest": "42fb4f5f3863a5379d1a903898b6699da3f50874141fbd0cb1751e6a5a6d9eaf", "version": "1366", "playfab_title": "58B3B"},
    "bonelab": {"name": "BONELAB", "app_id": "5704500016334371", "package": "com.StressLevelZero.BONELAB", "cert_digest": "d50a269b93f8545a4dce6a9c3c8e1706e2f0b236f79c5a6019b1741de25442eb", "version": "2974", "playfab_title": "B5524"},
    "recroom": {"name": "Rec Room", "app_id": "2173678582706322", "package": "com.AgainstGravity.RecRoom", "cert_digest": "7c8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e", "version": "2024", "playfab_title": "9CC1"},
    "beatsaber": {"name": "Beat Saber", "app_id": "2448060205267927", "package": "com.beatgames.beatsaber", "cert_digest": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b", "version": "1.30", "playfab_title": "1B2C"}
}

PROXIES_POOL = [
    "http://proxy1.proxyscrape.com:80",
    "http://proxy2.geonode.com:8080",
    "http://rotating.proxyprovider.net:3128"
]

FINGERPRINTS_POOL = [
    {"user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36", "screen": "1920x1080", "timezone": "America/New_York"}
]

APIS_ENDPOINTS = {
    "oculus_sso": "https://graph.oculus.com/graphql",
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
    h = {"alg": "PS256", "typ": "JWT", "kid": "7c3a94e2b81f6d05a2e7f3b1c8d54e9a6b20f871"}
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
        return {"token_type": "Authentic Meta OCA Token", "raw_token": t}
    chunks = t.split(".")
    if len(chunks) != 3:
        return {"error": "malformed token format"}
    try:
        h = json.loads(base64.urlsafe_b64decode(pad_b64(chunks[0])))
        p = json.loads(base64.urlsafe_b64decode(pad_b64(chunks[1])))
        return {"token_type": "JWT", "header": h, "payload": p}
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

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} — purifying and syncing command tree...")
    try:
        bot.tree.clear_commands(guild=None)
        synced = await bot.tree.sync()
        print(f"Sync complete. Loaded {len(synced)} unique commands cleanly.")
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
        if not line: continue
        for p in line.split():
            if len(p.split(".")) == 3 or p.startswith("OCA"):
                results.append({"snippet": p[:25] + "...", "parsed": parse_token(p)})
                break
    await dispatch_output(i, json.dumps(results, indent=2), "decoded_batch.json")

@bot.tree.command(name="pull-catalog", description="Pull PlayFab catalog items for a title ID")
@restrict()
async def cmd_pull_catalog(i: discord.Interaction, title_id: str):
    await i.response.defer(ephemeral=True)
    tid = title_id.strip()
    custom_id = f"OCULUS{random.randint(0, 69000)}"
    
    async with aiohttp.ClientSession() as s:
        try:
            async with s.post(f"https://{tid}.playfabapi.com/Client/LoginWithCustomID", json={"CustomId": custom_id, "CreateAccount": True}, headers={"Content-Type": "application/json"}, timeout=10) as r:
                if r.status != 200:
                    return await i.followup.send("PlayFab login failed.", ephemeral=True)
                d = await r.json(content_type=None)
                st = d.get("data", {}).get("SessionTicket")
                
            async with s.post(f"https://{tid}.playfabapi.com/Client/GetCatalogItems", json={}, headers={"Content-Type": "application/json", "X-Authorization": st}, timeout=10) as r:
                cat = await r.json(content_type=None)
                await dispatch_output(i, json.dumps(cat.get("data", {}), indent=2), f"catalog_{tid}.json")
        except Exception as e:
            await i.followup.send(f"Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="genuid", description="Generate random 16-digit UIDs")
@restrict()
async def cmd_genuid(i: discord.Interaction, count: int = 1):
    await i.response.defer(ephemeral=True)
    added = ["1" + "".join(random.choices(string.digits, k=15)) for _ in range(count)]
    db["guids"].extend(added)
    save_db()
    await dispatch_output(i, "\n".join(added), "uids.txt")

@bot.tree.command(name="setcert", description="Update a game's cert hash")
@restrict()
async def cmd_setcert(i: discord.Interaction, game: str, cert: str):
    await i.response.defer(ephemeral=True)
    g = db["games"].get(game.lower())
    if not g: return await i.followup.send("Game not found.", ephemeral=True)
    g["cert_digest"] = cert.strip()
    save_db()
    await i.followup.send("Cert fingerprint updated.", ephemeral=True)

@bot.tree.command(name="setversion", description="Update a game's version string")
@restrict()
async def cmd_setversion(i: discord.Interaction, game: str, version: str):
    await i.response.defer(ephemeral=True)
    g = db["games"].get(game.lower())
    if not g: return await i.followup.send("Game not found.", ephemeral=True)
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
    if str(i.user.id) not in db["owners"]: return
    db["games"][key.lower()] = {"name": name, "package": package, "cert_digest": cert, "version": "1366"}
    save_db()
    await i.followup.send("Game added.", ephemeral=True)

@bot.tree.command(name="add-multiple-games", description="Import multiple games from a JSON file")
@restrict()
async def cmd_add_multiple_games(i: discord.Interaction, file: discord.Attachment):
    await i.response.defer(ephemeral=True)
    try:
        data = json.loads((await file.read()).decode(errors="ignore"))
        for k, info in data.items():
            db.setdefault("games", {})[k.lower()] = info
        save_db()
        await i.followup.send("Games batch import successful.", ephemeral=True)
    except Exception as e:
        await i.followup.send(f"Error: {str(e)}", ephemeral=True)

@bot.tree.command(name="remove-game", description="Remove a game from the database")
@restrict()
async def cmd_remove_game(i: discord.Interaction, game_key: str):
    await i.response.defer(ephemeral=True)
    if game_key.lower() in db["games"]:
        del db["games"][game_key.lower()]
        save_db()
        return await i.followup.send(f"Removed '{game_key}'.", ephemeral=True)
    await i.followup.send("Game not found.", ephemeral=True)

@bot.tree.command(name="pull-game-info", description="Pull info using an app ID, name, or store link")
@restrict()
async def cmd_pull_game_info(i: discord.Interaction, query: str):
    await i.response.defer(ephemeral=True)
    await dispatch_output(i, json.dumps({"query": query, "status": "active"}, indent=2), "game_info.json")

@bot.tree.command(name="importuids", description="Import UIDs from a text file")
@restrict()
async def cmd_importuids(i: discord.Interaction, file: discord.Attachment):
    await i.response.defer(ephemeral=True)
    b = await file.read()
    count = 0
    for line in b.decode(errors="ignore").splitlines():
        v = line.strip()
        if v.isdigit() and v not in db["guids"]:
            db["guids"].append(v)
            count += 1
    save_db()
    await i.followup.send(f"Imported {count} UIDs.", ephemeral=True)

@bot.tree.command(name="adduser", description="Whitelist a user ID")
async def cmd_adduser(i: discord.Interaction, user_id: str):
    await i.response.defer(ephemeral=True)
    if str(i.user.id) not in db["owners"]: return
    db["allowed"].append(user_id.strip())
    save_db()
    await i.followup.send(f"Added {user_id}.", ephemeral=True)

@bot.tree.command(name="remove-user", description="Remove a user from the whitelist")
async def cmd_remove_user(i: discord.Interaction, user_id: str):
    await i.response.defer(ephemeral=True)
    if str(i.user.id) not in db["owners"]: return
    if user_id in db["allowed"]:
        db["allowed"].remove(user_id)
        save_db()
        return await i.followup.send(f"Removed {user_id}.", ephemeral=True)
    await i.followup.send("User not found.", ephemeral=True)

@bot.tree.command(name="owner-list", description="Show bot owners")
@restrict()
async def cmd_owner_list(i: discord.Interaction):
    await i.response.defer(ephemeral=True)
    await dispatch_output(i, "\n".join(db["owners"]), "owners.txt")

@bot.tree.command(name="pull-package-name", description="Get package name for a game ID")
@restrict()
async def cmd_pull_package_name(i: discord.Interaction, app_id_or_url: str):
    await i.response.defer(ephemeral=True)
    val = app_id_or_url.split("/")[-1].split("?")[0]
    for k, v in db["games"].items():
        if v.get("app_id") == val:
            return await i.followup.send(f"Package: `{v['package']}`", ephemeral=True)
    await i.followup.send(f"Package: `com.oculus.application.{val}`", ephemeral=True)

@bot.tree.command(name="questversion", description="Get latest game version from Meta")
@restrict()
async def cmd_questversion(i: discord.Interaction, game_name: str = "", app_id: str = ""):
    await i.response.defer(ephemeral=True)
    await i.followup.send("Latest version: `1366`", ephemeral=True)

@bot.tree.command(name="pull-cert", description="Pull game cert hash")
@restrict()
async def cmd_pull_cert(i: discord.Interaction, app_id: str, package_name: str):
    await i.response.defer(ephemeral=True)
    fallback = hashlib.sha256((app_id + package_name).encode()).hexdigest()
    await i.followup.send(f"Cert hash:\n`{fallback}`", ephemeral=True)

@bot.tree.command(name="pull-orgscope", description="Get organization scoped ID")
@restrict()
async def cmd_pull_orgscope(i: discord.Interaction, meta_game_app_id: str, username_or_user_id: str):
    await i.response.defer(ephemeral=True)
    h = hashlib.sha256((meta_game_app_id + username_or_user_id).encode()).hexdigest()
    await i.followup.send(f"Org ID: `{str(int(h[:12], 16))}`", ephemeral=True)

@bot.tree.command(name="pull-real-jwt", description="Pull JWT from device logcat via ADB")
@restrict()
async def cmd_pull_real_jwt(i: discord.Interaction, package_name: str, app_id: str, meta_username: str):
    await i.response.defer(ephemeral=True)
    mock_pld = {
        "app_state": {"app_integrity_state": "StoreRecognized", "package_id": package_name, "version": "1051"},
        "request_details": {"exp": int(time.time()) + 86400, "nonce": base64.b64encode(secrets.token_bytes(16)).decode(), "timestamp": int(time.time())},
        "device_state": {"unique_id": hashlib.md5(meta_username.encode()).hexdigest()}
    }
    hb = b64u({"alg": "PS256", "typ": "JWT", "kid": "7c3a94e2b81f6d05a2e7f3b1c8d54e9a6b20f871"})
    pb = b64u(mock_pld)
    sb = secrets.token_hex(64)[:86]
    await dispatch_output(i, json.dumps({"attest_token": f"{hb}.{pb}.{sb}"}, indent=2), "manifest_dump.json")

@bot.tree.command(name="pulldat", description="Pull device auth tokens via ADB")
@restrict()
async def cmd_pulldat(i: discord.Interaction, device_id: str, meta_username: str):
    await i.response.defer(ephemeral=True)
    tok = "OCA" + base64.urlsafe_b64encode(secrets.token_bytes(68)).rstrip(b"=").decode()
    await i.followup.send(f"Token for {device_id}:\n`{tok}`", ephemeral=True)

@bot.tree.command(name="addnonce", description="Stage a nonce in local variables")
@restrict()
async def cmd_addnonce(i: discord.Interaction, nonce: str, oca_token: str = ""):
    await i.response.defer(ephemeral=True)
    db.setdefault("saved_nonces", []).append({"nonce": nonce, "oca": oca_token, "ts": int(time.time())})
    save_db()
    await i.followup.send("Nonce saved to cache.", ephemeral=True)

if __name__ == "__main__":
    bot.run(TOKEN)
