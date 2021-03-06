import random
import net
from logging import getLogger
from constants import *

log = getLogger(__name__)

# shouldn't mix async and sync methods!!

class Player:

    def __init__(self, stream):
        self.username = None
        self.stream = stream
        self.pos = None

        self.color = [
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        ]

        # 0 top, 1 right, 2 bottom and 3 is left
        self.weak_side = random.randint(0, 3)

        self.keyboard_state = 0

    async def get_username(self):
        resp = await self.stream.read()

        if resp['type'] != 'username':
            raise ValueError(f"invalid response: type should be 'username' in {resp}")

        if 'username' not in resp:
            raise ValueError(f"invalid response: 'username' key should be set in {resp}")

        self.username = resp['username']
        log.info(f"Player got username: {self.username}")

    def spawn(self, pos):
        if self.is_on_map:
            raise RuntimeError("player already spawned")
        self.pos = list(pos)

    def collides(self, target):
        p = self.pos
        t = target.pos
        w = PLAYER_SIZE[0]
        h = PLAYER_SIZE[1]
        return (
            (
                # target left side between player left and right
                p[0] <= t[0] <= p[0] + w
                # target top side between player top and bottom
                and p[1] <= t[1] <= p[1] + h
            ) or (
                # target right side between player left and right
                p[0] <= t[0] + w <= p[0] + w
                # target top side between player top and bottom
                and p[1] <= t[1] + h <= p[1] + h
            )
        )

    async def get_user_input_forever(self):
        log.info(f"{self} Listening for user input")
        while True:
            resp = await self.stream.read()
            if resp['type'] != 'keyboard':
                raise ValueError(f"Expected type='keyboard' in {resp}")
            self.keyboard_state = resp['state']

    async def killed(self):
        await self.stream.write({
            "type": "dead"
        })

    def move(self, loop_time):
        """ Move according to the keyboard state """
        if self.keyboard_state & LEFT:
            self.pos[0] -= PLAYER_SPEED * loop_time
        if self.keyboard_state & RIGHT:
            self.pos[0] += PLAYER_SPEED * loop_time
        if self.keyboard_state & UP:
            self.pos[1] -= PLAYER_SPEED * loop_time
        if self.keyboard_state & DOWN:
            self.pos[1] += PLAYER_SPEED * loop_time

    @property
    def is_on_map(self):
        return self.pos is not None

    def state_for_initialization(self):
        """ State information that is send only once """
        return {
            "pos": self.pos,
            "color": self.color
        }

    def state_for_update(self):
        """ State information that is send every update """
        return {
            "pos": self.pos
        }

    def __str__(self):
        return f"<s.Player {self.username!r} {self.color}>"

    def __repr__(self):
        return str(self)