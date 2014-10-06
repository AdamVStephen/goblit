import pygame
from pygame.font import Font
from .animations import Sequence, Frame, Animation, loop
from .loaders import load_image


GOBLIT = Animation({
    'default': Sequence([
        Frame(load_image('goblit-standing'), (-18, -81))
    ], loop)
})

TOX = Animation({
    'default': Sequence([
        Frame(load_image('tox-standing'), (-31, -95))
    ], loop),
    'sitting-at-desk': Sequence([
        Frame(load_image('tox-sitting-desk'), (-37, -99))
    ], loop),
    'sitting': Sequence([
        Frame(load_image('tox-sitting'), (-41, -91))
    ], loop)
})

FONT_NAME = 'fonts/RosesareFF0000.ttf'
FONT = Font(FONT_NAME, 16)


class FontBubble:
    def __init__(self, text, pos=(0, 0), color=(255, 255, 255)):
        self.text = text
        self.pos = pos
        self.color = color
        self._build_surf()

    def _build_surf(self):
        base = FONT.render(self.text, False, self.color)
        black = FONT.render(self.text, False, (0, 0, 0))

        w, h = base.get_size()
        self.surf = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)

        for off in [(0, 0), (0, 2), (2, 0), (2, 2)]:
            self.surf.blit(black, off)

        self.surf.blit(base, (1, 1))

    def draw(self, screen):
        x, y = self.pos
        w = self.surf.get_width()
        x = min(max(10, x - w // 2), 950 - w)
        screen.blit(self.surf, (x, y))


class SpeechBubble(FontBubble):
    def __init__(self, text, actor):
        x, y = actor.sprite.pos
        super().__init__(text, (x, y - 120), actor.COLOR)


class ActorMeta(type):
    def __new__(cls, name, bases, dict):
        stage_directions = {}
        for b in reversed(bases):
            try:
                stage_directions.update(b.stage_directions)
            except AttributeError:
                pass
        for k, v in list(dict.items()):
            if callable(v):
                verb = getattr(v, 'stage_direction', None)
                if verb:
                    stage_directions[verb] = v

        dict['stage_directions'] = stage_directions
        return type.__new__(cls, name, bases, dict)


def stage_direction(name):
    """Decorator to mark a method as a stage direction."""
    def decorator(func):
        func.stage_direction = name
        return func
    return decorator


class Actor(metaclass=ActorMeta):
    def __init__(self, pos, dir='right', initial='default'):
        self.sprite = self.SPRITE.create_instance(pos)
        self.sprite.dir = 'right'
        self.words = None
        self.sprite.play(initial)

    def draw(self, screen):
        self.sprite.draw(screen)

    @stage_direction('enters')
    def enter(self):
        raise NotImplementedError("Enter is not implemented")

    @stage_direction('leaves')
    def leave(self):
        raise NotImplementedError("Leave is not implemented")


class Goblit(Actor):
    COLOR = (255, 255, 255)
    SPRITE = GOBLIT


class Tox(Actor):
    COLOR = (180, 50, 255)
    SPRITE = TOX

    @stage_direction('turns around')
    def turn_around(self):
        self.sprite.play('sitting')
        self.sprite.dir = 'left'

    @stage_direction('turns back to desk')
    def turn_back_to_desk(self):
        self.sprite.play('sitting-at-desk')
        self.sprite.dir = 'right'