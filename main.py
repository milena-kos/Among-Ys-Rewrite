import random, math, os, pygame, requests, sys, logging, socket, threading, json, ast, traceback, tasks, utils
import tkinter as tk


class Client:
    def __init__(self, host, port):
        self.info = None

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))

        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

    def receive(self):
        while True:
            message = self.sock.recv(4096)
            if message:
                try:
                    self.info = json.loads(message)
                except Exception as e:
                    print(e)

    def write(self, data):
        self.sock.send(json.dumps(data).encode("utf-8"))

    def close(self):
        self.sock.close()

    def get(self):
        return self.info


class Name(pygame.sprite.Sprite):
    def __init__(self, name, is_sus):
        if is_sus:
            color = 0
        else:
            color = 255
        self.name = name
        pygame.sprite.Sprite.__init__(self)
        self.font = pygame.font.Font(utils.get_path("arlrdbd.ttf"), 35)
        self.textSurf = self.font.render(name, 5, (255, color, color))
        self.image = pygame.Surface((1280, 720))
        W = self.textSurf.get_width()
        H = self.textSurf.get_height()
        self.image.blit(self.textSurf, [640 - W / 2, 280 - H / 2])
        self.image.set_colorkey((0, 0, 0))
        self.rect = self.image.get_rect()

    def update(self, where, screen):
        self.rect.center = where
        screen.blit(self.image, self.rect)

    def get_name(self):
        logging.info("Class Name: Returning %s...", self.name)
        return self.name


class Crew(pygame.sprite.Sprite):
    def __init__(self, colors, name):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(
            utils.get_path("img/crew/" + colors + ".png")
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image, (74, 99))
        self.rect = self.image.get_rect()
        self.rect.center = (640, 360)
        self.x = 640
        self.y = 360
        self.orient = "Left"
        self.shadow = pygame.image.load(
            utils.get_path("img/shadow.png")
        ).convert_alpha()

        self.color = colors
        if name != "":
            self.nickname = name
            self.name = Name(name, True)
        else:
            self.name = False

    def update(self, orient, *args):
        self.orient = orient
        if args:
            self.x = args[0]
            self.y = args[1]

    def draw(self, screen, *args):
        if args:
            self.rect.center = (args[0] - self.x + 640, args[1] - self.y + 360)
        self.name.update(self.rect.center, screen)
        screen.blit(self.shadow, (640 - 37, 390))
        if self.orient == "Right":
            screen.blit(self.image, self.rect)
        elif self.orient == "Left":
            screen.blit(pygame.transform.flip(self.image, True, False), self.rect)


class Bot(pygame.sprite.Sprite):
    def __init__(self, idd, colors, names, ticks):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(
            utils.get_path("img/crew/" + random.choice(colors) + ".png")
        ).convert_alpha()
        self.image = pygame.transform.scale(self.image, (74, 99))
        self.rect = self.image.get_rect()
        self.rect.center = (640, 360)
        self.moves = ast.literal_eval(
            open(utils.get_path("moves\\file" + str(idd) + ".txt"), "r").read()
        )
        self.my_name = random.choice(names)
        self.name = Name(self.my_name, False)
        names.remove(self.my_name)
        self.ticks = ticks
        self.shadow = pygame.image.load(
            utils.get_path("img/shadow.png")
        ).convert_alpha()

    def update(self, x, y, screen, orient, do_drawing=True):
        self.ticks += 1
        try:
            self.rect.center = (
                x - self.moves[self.ticks][0] + 640,
                y - self.moves[self.ticks][1] + 360,
            )
            if do_drawing:
                self.name.update(self.rect.center, screen)
                screen.blit(self.shadow, (self.rect.x, self.rect.y + 80))
                if self.moves[self.ticks][2] == "Right":
                    screen.blit(self.image, self.rect)
                else:
                    screen.blit(
                        pygame.transform.flip(self.image, True, False), self.rect
                    )
        except IndexError:
            self.ticks = 0

    def distance_from_center(self):  # sorry i wont put centre because why
        return math.hypot(640 - self.rect.x, 360 - self.rect.y)

    def get_coords(self):
        return self.moves[self.ticks][0], self.moves[self.ticks][1]


def game(player_name, player_color, is_multiplayer, d):

    ############################
    # DEFINE STUFF
    ############################

    v = "v2.3.2"

    logging.info("Loading pygame...")

    pygame.init()
    pygame.font.init()

    vis_coff = 2

    logging.info("Loading variables...")

    (
        client,
        rush,
        walls_mask,
        hitbox_mask,
        chat_opened,
        kill_btn,
        counter,
        back,
        crew,
        message_done,
        message_text,
        log_text,
    ) = (
        0,
        "",
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        "",
        "",
        "",
    )  # to fix "Referenced before assigment" errors

    do_kill, do_write, do_ping_pong, kill_possible, running, loading, rush_active = (
        False,
        False,
        False,
        True,
        True,
        False,
        False,
    )

    ticks, FPS, x, y, change, old_super, kill_save = 0, 120, -2800, -450, 15, -1, -120

    orient = "Left"

    names = [
        "Milenakos",
        "Allleeeeeccccccc",
        "APaplsa",
        "Aurelia",
        "Axolotl in a bucket",
        "Banana Monster",
        "suffix.",
        "SpaceCell",
        "Frinkifail",
        "Xiaoness191",
        "m(._.)m",
        "isMatteo",
        "Kokomichii~",
        "Lkmanisnew",
        "lxgit",
        "=/",
        "moneyhacker",
        "NathanCrazy",
        "og",
        "SOKE",
        "Totally Not Milenakos",
        "Tully",
        "WarNoodleZ",
        "Yuuta Togashi",
    ]

    colors = {
        "Red": (179, 10, 32),
        "Blue": (19, 46, 209),
        "Green": (17, 127, 44),
        "Pink": (237, 84, 186),
        "Orange": (239, 125, 14),
        "Yellow": (246, 246, 88),
        "Black": (62, 71, 78),
        "White": (214, 224, 240),
        "Purple": (107, 49, 188),
        "Brown": (113, 73, 30),
        "Cyan": (56, 254, 219),
        "Lime": (80, 239, 57),
        "Maroon": (108, 43, 61),
        "Rose": (236, 192, 211),
        "Banana": (254, 253, 189),
        "Gray": (112, 132, 151),
        "Tan": (146, 135, 118),
        "Coral": (236, 117, 120),
        "Olive": (97, 114, 24),
        "Fortegreen": (29, 151, 83),
    }

    moves, bots, players, loading2 = [], [], [], []

    ############################
    # INIT
    ############################

    logging.info("Creating game window...")
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("Among Ys Rewrite")
    clock = pygame.time.Clock()
    pygame.mixer.init()

    logging.info("Rendering first frame...")
    font = pygame.font.Font(utils.get_path("arlrdbd.ttf"), 30)
    font1 = pygame.font.Font(utils.get_path("arlrdbd.ttf"), 35)
    loading = font.render("Loading images...", 5, (255, 255, 255))

    screen.fill((0, 0, 0))

    screen.blit(loading, (5, 680))

    pygame.display.set_icon(pygame.image.load(utils.get_path("img/icon.png")))

    pygame.display.flip()

    ############################
    # MAIN LOOP
    ############################

    while running:
        clock.tick(FPS)
        ticks += 1

        ############################
        # CHECK FOR INPUTS
        ############################

        do_kill = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                logging.info("Got exit signal.")
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    try:
                        piano.render(event.pos)
                    except Exception:
                        pass
                    if (
                        kill_btn.collidepoint(event.pos)
                        and not chat_opened
                        and not is_multiplayer
                    ):
                        logging.info("Got mouse press signal.")
                        do_kill = True

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    try:
                        piano.render((0, 0))
                    except Exception:
                        pass

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q and not is_multiplayer:
                    if not chat_opened:
                        logging.info("Got Q press signal.")
                        do_kill = True

                if event.key == pygame.K_p and not is_multiplayer and not chat_opened:
                    logging.info(
                        "Ping pong state was %s, now vice-versa.", str(do_ping_pong)
                    )
                    if do_ping_pong:
                        do_ping_pong = False
                    else:
                        do_ping_pong = True

                if chat_opened:
                    if event.key == pygame.K_RETURN:
                        logging.info(f"{message_text} was sent by me!")
                        message_done = message_text
                        message_text = ""
                    elif event.key == pygame.K_BACKSPACE:
                        message_text = message_text[:-1]
                    else:
                        message_text = str(message_text) + event.unicode

                if event.key == pygame.K_RETURN and is_multiplayer:
                    if chat_opened:
                        chat_opened = False
                    else:
                        chat_opened = True

        if ticks != 1:

            ############################
            # KILL BOTS
            ############################

            if do_kill and kill_possible and not is_multiplayer:
                logging.info("Killing...")
                dists = []
                for i in bots:
                    dists.append(i.distance_from_center())
                if min(dists) <= 100 and ticks - kill_save > 120:
                    enemy_ind = dists.index(min(dists))
                    enemy = bots[enemy_ind]
                    x, y = enemy.get_coords()
                    logging.info(
                        "Bot %s was killed, with name %s.", enemy_ind, enemy.my_name
                    )
                    bots.pop(enemy_ind)
                    kill_save = ticks
                    logging.info(
                        "%s people left, rendering counter.", str(len(bots) + 1)
                    )
                    textSurf = font.render(
                        "People left: " + str(len(bots) + 1), 5, (255, 255, 255)
                    )
                    counter = pygame.Surface((1280, 720))
                    counter.blit(textSurf, [0, 0])
                    counter.set_colorkey((0, 0, 0))
                else:
                    logging.info("No bots in kill distance or kill cooldown is active.")
                do_kill = False
                if len(bots) == 0:
                    logging.info("All bots killed.")
                    kill_possible = False

            ############################
            # MOVE PLAYER
            ############################

            keys = pygame.key.get_pressed()

            new_x = new_y = 0

            if keys[pygame.K_r] and rush == "":
                rush = "r"
            if keys[pygame.K_u] and rush == "r":
                rush = "ru"
            if keys[pygame.K_s] and rush == "ru":
                rush = "rus"
            if keys[pygame.K_h] and rush == "rus":
                rush = "rush"
            print(rush)
            if (
                rush == "rush"
                and not rush_active
                and not is_multiplayer
                and not chat_opened
            ):
                rush_active = True
                pygame.mixer.music.load(utils.get_path("sounds/rush_e_1.mp3"))
                pygame.mixer.music.play()

            if not (
                keys[pygame.K_r]
                or keys[pygame.K_u]
                or keys[pygame.K_s]
                or keys[pygame.K_h]
            ):
                rush = ""

            if pygame.mixer.music.get_busy() != True and rush_active:
                raise RushE

            if do_ping_pong:
                if do_ping_pong == True:
                    do_ping_pong = random.randint(1, 8)
                if do_ping_pong == 1:
                    new_x += change
                elif do_ping_pong == 2:
                    new_x -= change
                elif do_ping_pong == 3:
                    new_y += change
                elif do_ping_pong == 4:
                    new_y -= change
                elif do_ping_pong == 5:
                    new_y -= change
                    new_x -= change
                elif do_ping_pong == 6:
                    new_y -= change
                    new_x += change
                elif do_ping_pong == 7:
                    new_y += change
                    new_x -= change
                elif do_ping_pong == 8:
                    new_y += change
                    new_x += change
                return new_x, new_y
            elif not chat_opened:
                if keys[pygame.K_a] or keys[pygame.K_LEFT]:
                    new_x += change
                if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
                    new_x -= change

                if keys[pygame.K_w] or keys[pygame.K_UP]:
                    new_y += change
                if keys[pygame.K_s] or keys[pygame.K_DOWN]:
                    new_y -= change

            if new_x > 0:
                orient = "Left"
            elif new_x < 0:
                orient = "Right"

            x_save, y_save = x, y

            x += new_x
            y += new_y

            if do_write and not is_multiplayer:
                moves.append([x, y, orient])

            if walls_mask.overlap(hitbox_mask, (-x, -y)):
                x, y = x_save, y_save
                if do_ping_pong:
                    old_super = do_ping_pong
                    while do_ping_pong == old_super:
                        do_ping_pong = random.randint(1, 8)
                    logging.info("New ping pong direction, %s.", do_ping_pong)

            ############################
            # UPDATE MULTIPLAYER
            ############################

            if ticks > 4 and is_multiplayer:
                info = client.get()
                print(info)
                if info != None:
                    if info[0] != player_name:
                        if (
                            isinstance(info, list)
                            and len(info) == 2
                            and info[0] != player_name
                            and info[1] != player_color
                        ):
                            new = Crew(info[1], info[0])
                            players.append(new)
                        if isinstance(info, list) and len(info) == 4:
                            for j in players:
                                if info[0] == j.nickname:
                                    j.update(info[3], info[1], info[2])
                                    break
                            if info[4] != "":
                                line = info[0] + ": " + info[4] + "\n"
                                log_text.append(line)
                client.write([player_name, x, y, orient, message_done])
                if message_done != "":
                    line = player_name + ": " + message_done + "\n"
                    log_text.append(line)
                    message_done = ""

        ############################
        # LOADINGS
        ############################

        if ticks == 1:
            logging.info("Loading images...")
            walls = pygame.image.load(utils.get_path("img/layout.png"))
            walls_mask = pygame.mask.from_surface(walls)

            hitbox = pygame.image.load(utils.get_path("img/hitbox.png"))
            hitbox_mask = pygame.mask.from_surface(hitbox)

            kill = pygame.image.load(utils.get_path("img/kill.png"))
            kill_btn = kill.get_rect()
            kill_btn.center = (1200, 640)

            overlay = pygame.image.load(utils.get_path("img/overlay.png"))
            overlay = pygame.transform.scale(
                overlay, (math.ceil(1280 * vis_coff), math.ceil(720 * vis_coff))
            )

            back = pygame.image.load(utils.get_path("img/skeld.png"))
            crew = Crew(player_color, player_name)

            # piano = tasks.Piano_task()

            logging.info("Checking for updates...")
            loading = [font.render("Checking for updates...", 5, (255, 255, 255))]
        elif ticks == 2:
            try:
                latest = requests.get(
                    "https://api.github.com/repos/milena-kos/Among-Ys-Rewrite/releases/latest"
                ).text
                version = json.loads(latest)["name"]
            except Exception as e:
                logging.warning("Failed to check version.")
                version = None
            logging.info("Loading players...")
            loading = [font.render("Loading players...", 5, (255, 255, 255))]
        elif ticks == 3 and is_multiplayer:
            try:
                if is_multiplayer == "":
                    raise ValueError
                HOST, PORT = is_multiplayer.split(":")
                client = Client(HOST, int(PORT))
                client.write([player_name, player_color])
                ip_error = False
            except ValueError:
                print(is_multiplayer)
                is_multiplayer = False
                ip_error = True
                if not do_write:
                    for i in range(0, len(os.listdir(utils.get_path("moves")))):
                        bots.append(Bot(i, list(colors.keys()), names, ticks))

            logging.info("Loading text...")
            loading = [font.render("Loading text...", 5, (255, 255, 255))]
        elif ticks == 3 and not is_multiplayer:
            ip_error = False
            if not do_write:
                for i in range(0, len(os.listdir(utils.get_path("moves")))):
                    bots.append(Bot(i, list(colors.keys()), names, ticks))
            logging.info("Loading text...")
            loading = [font.render("Loading text...", 5, (255, 255, 255))]
        elif ticks == 4 and not is_multiplayer:
            logging.info("Rendering counter...")
            textSurf = font1.render(
                "People left: " + str(len(bots) + 1), 5, (255, 255, 255)
            )
            counter = pygame.Surface((1280, 720))
            counter.blit(textSurf, [0, 0])
            counter.set_colorkey((0, 0, 0))
        if ticks == 4:
            log_text = []
            if d == True:
                log_text.append("Failed to start logging..")
            if ip_error:
                log_text.append("Server is down! Starting in singleplayer....")
            if (
                version
                and version != v
                and getattr(sys, "frozen", False)
                and hasattr(sys, "_MEIPASS")
            ):
                logging.warning("Using old version of Among Ys Rewrite.")
                log_text.append(
                    "New version of Among Ys Rewrite is available. Please upgrade your game.."
                )

        ############################
        # UPDATE CHAT
        ############################

        if ticks > 5:
            loading = []
            loading2 = []
            for i in log_text[::-1]:
                try:
                    a = i.split(":")
                    colora = (255, 255, 255)
                    for j in players:
                        if j.username == a[0]:
                            colora = j.color
                    if a[0] == player_name:
                        colora = player_color
                except Exception:
                    colora = (255, 255, 255)
                loading.append(font.render(i[:-1], 5, colora))
                loading2.append(font.render(i[:-1], 5, (0, 0, 0)))

        ############################
        # RENDER
        ############################

        screen.fill((0, 0, 0))
        chat_offset = 0

        if ticks > 4:
            screen.blit(back, (x, y))
            for i in bots:
                do_draw = True
                if i.distance_from_center() > 200 * vis_coff:
                    do_draw = False
                i.update(x, y, screen, orient, do_draw)
            for i in players:
                i.draw(screen, x, y)
            crew.update(orient)
            crew.draw(screen)
            walls.get_rect().center = (x, y)
            screen.blit(
                overlay,
                (
                    1280 - (1280 * vis_coff) + (1280 * vis_coff * 0.25),
                    720 - (720 * vis_coff) + (720 * vis_coff * 0.25),
                ),
            )
            if not is_multiplayer:
                screen.blit(counter, (0, 0))
                if kill_possible:
                    screen.blit(kill, kill_btn)
            try:
                piano.draw(screen)
                if piano.finished:
                    piano = None
            except Exception:
                pass
        if ticks > 4 and chat_opened:
            pygame.draw.rect(screen, (255, 255, 255), (10, 660, 500, 50))
            pygame.draw.rect(screen, (0, 0, 0), (10, 660, 500, 50), 5)
            textSurf = font.render(str(message_text) + "|", 5, (0, 0, 0))
            message = pygame.Surface((1280, 720))
            message.fill((255, 255, 255))
            message.blit(textSurf, [0, 0])
            message.set_colorkey((255, 255, 255))
            screen.blit(message, (20, 660))
            chat_offset += 70
        if loading:
            for num, i in enumerate(loading2):
                x_ = 5
                y_ = 680 - chat_offset - (num * 35)
                screen.blit(i, (x_ + 2, y_ + 2))
                screen.blit(i, (x_ + 2, y_ - 2))
                screen.blit(i, (x_ - 2, y_ + 2))
                screen.blit(i, (x_ - 2, y_ - 2))
                screen.blit(i, (x_, y_ + 2))
                screen.blit(i, (x_, y_ - 2))
                screen.blit(i, (x_ - 2, y_))
                screen.blit(i, (x_ + 2, y_))
            for num, i in enumerate(loading):
                screen.blit(i, (5, 680 - chat_offset - (num * 35)))

        pygame.display.flip()

    if do_write:
        file = open("moves\\file.txt", "w")
        file.write(str(moves))
        file.close()

    if is_multiplayer:
        client.close()

    logging.info("Quitting pygame...")
    pygame.quit()


def character_limit(nickname):
    if len(nickname.get()) > 15:
        logging.info("Over 15 characters, limiting...")
        nickname.set(nickname.get()[:15])


def settings(d):

    ############################
    # LOAD SETTINGS
    ############################

    if not os.path.exists(os.getenv("LOCALAPPDATA") + "\\Milenakos\\AmongYsRewrite"):
        os.makedirs(os.getenv("LOCALAPPDATA") + "\\Milenakos\\AmongYsRewrite")
    try:
        pref = json.load(
            open(
                os.getenv("LOCALAPPDATA")
                + "\\Milenakos\\AmongYsRewrite\\settings.json",
                "r",
            )
        )
    except Exception:
        logging.warning("Failed to load settings.json!")
        pref = False

    master = tk.Tk()
    c = False
    master.title("Settings")

    icon = tk.PhotoImage(file=utils.get_path("img\icon.png"))
    master.iconphoto(True, icon)

    logging.info("Loaded! Adding buttons...")
    tk.Label(master, text="Among Ys Settings").grid(row=0)
    tk.Label(master, text="Your name").grid(row=1, column=0)
    tk.Label(master, text="Your color").grid(row=2, column=0)

    color = tk.StringVar()
    nickname = tk.StringVar()

    color.set("Red")
    if pref:
        nickname.set(pref["nickname"])
        color.set(pref["color"])

    e1 = tk.Entry(master, textvariable=nickname)
    e2 = tk.OptionMenu(
        master,
        color,
        "Red",
        "Blue",
        "Green",
        "Pink",
        "Orange",
        "Yellow",
        "Black",
        "White",
        "Purple",
        "Brown",
        "Cyan",
        "Lime",
        "Maroon",
        "Rose",
        "Banana",
        "Gray",
        "Tan",
        "Coral",
        "Olive",
        "Fortegreen",
    )
    e1.grid(row=1, column=1)
    e2.grid(row=2, column=1)

    def online():
        nonlocal c
        c = requests.get("https://among-ys.glitch.me/current-server.html").text
        master.destroy()

    def quit_tk():
        master.destroy()
        sys.exit()

    tk.Button(master, text="Online", width=15, command=online).grid(row=4, column=1)
    tk.Button(master, text="Offline", width=15, command=master.destroy).grid(
        row=4, column=0
    )

    master.protocol("WM_DELETE_WINDOW", quit_tk)

    logging.info("Done! Waiting for input...")
    nickname.trace("w", lambda *args: character_limit(nickname))
    tk.mainloop()
    logging.info("Got input! Closing settings...")

    try:
        json.dump(
            {"nickname": nickname.get(), "color": color.get()},
            open(
                os.getenv("LOCALAPPDATA")
                + "\\Milenakos\\AmongYsRewrite\\settings.json",
                "w",
            ),
        )
    except Exception:
        logging.warning("Failed to save settings.json!")

    logging.info("Starting game...")
    game(nickname.get(), color.get(), c, d)


def main():
    ############################
    # CREATE LOGS
    ############################

    d = False
    try:
        os.remove("log.txt")
        logging.basicConfig(filename="log.txt", level=logging.INFO)
    except FileNotFoundError:
        logging.basicConfig(filename="log.txt", level=logging.INFO)
        logging.warning("Failed to delete log file!")
    except PermissionError:
        d = True

    ############################
    # CRASH REPORTER
    ############################

    try:
        logging.info("Loading settings window...")
        settings(d)
    except Exception as e:
        logging.warning("Got error! Analysing...")
        if e == 'can\'t invoke "destroy" command: application has been destroyed':
            logging.info("Aplication exit by user, no errors.")
        else:
            error = str(traceback.format_exc())

            if error[-39:].startswith("NameError: name 'RushE' is not defined"):
                error = "E"
                pygame.quit()

            logging.fatal(error)
            print(error)
            pygame.quit()

            logging.info("Starting rendering crash report window...")

            master = tk.Tk()
            master.title("Crash Report")

            logging.info("Loaded! Adding text...")
            tk.Label(
                master,
                text=f"Skill issue! Your game crashed.\n\n{error}\n\nFull crash log with details can be seen in log.txt file",
                justify="left",
            ).pack(pady=5)

            logging.info("Done!")

            if error == "E":

                def rush_e():
                    os.system(utils.get_path("sounds/rush_e_2.mp3"))

                x = threading.Thread(target=rush_e)
                x.start()

            tk.mainloop()


if __name__ == "__main__":
    main()
