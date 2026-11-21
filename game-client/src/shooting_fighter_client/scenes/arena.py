"""Simple built-in geometry arena using Ursina's Y-up coordinates."""


def build_arena() -> None:
    from ursina import AmbientLight, DirectionalLight, Entity, Sky, color

    Sky()
    Entity(
        model="cube",
        name="ground",
        scale=(40, 0.2, 40),
        position=(0, -0.1, 0),
        color=color.rgb(80, 100, 80),
        collider="box",
    )
    wall_color = color.rgb(75, 85, 110)
    walls = [
        ((0, 2.5, -20), (40, 5, 0.5)),
        ((0, 2.5, 20), (40, 5, 0.5)),
        ((-20, 2.5, 0), (0.5, 5, 40)),
        ((20, 2.5, 0), (0.5, 5, 40)),
    ]
    for position, scale in walls:
        Entity(model="cube", position=position, scale=scale, color=wall_color, collider="box")
    AmbientLight(color=color.rgba(120, 120, 120, 255))
    sun = DirectionalLight()
    sun.look_at((1, -2, -1))
