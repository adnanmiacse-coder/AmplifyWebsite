from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=40)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        parent_cell = Circle(radius=1, color=WHITE)
        parent_nucleus = Circle(radius=0.3, color=BLUE)
        parent_cell.add(parent_nucleus)

        self.play(Create(parent_cell), Create(parent_nucleus))
        self.wait(1)

        chromosomes = VGroup(*[Dot(point=parent_nucleus.get_center() + 0.2 * RIGHT).set_color(RED) for _ in range(4)])
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN) for c in chromosomes], lag_ratio=0.2))
        self.wait(1)

        duplicated_chromosomes = VGroup(*[Dot(point=parent_nucleus.get_center() + 0.2 * RIGHT).set_color(RED) for _ in range(8)])
        self.play(Transform(chromosomes, duplicated_chromosomes))
        self.wait(1)

        split_arrow = Arrow(start=parent_cell.get_top(), end=parent_cell.get_bottom(), buff=0)
        self.play(Create(split_arrow))
        self.wait(1)

        daughter_cell_1 = Circle(radius=0.8, color=WHITE).shift(LEFT*1.2)
        daughter_nucleus_1 = Circle(radius=0.25, color=BLUE).move_to(daughter_cell_1.get_center())
        daughter_chromosomes_1 = VGroup(*[Dot(point=daughter_nucleus_1.get_center() + 0.15 * RIGHT).set_color(RED) for _ in range(4)])
        daughter_cell_1.add(daughter_nucleus_1)

        daughter_cell_2 = Circle(radius=0.8, color=WHITE).shift(RIGHT*1.2)
        daughter_nucleus_2 = Circle(radius=0.25, color=BLUE).move_to(daughter_cell_2.get_center())
        daughter_chromosomes_2 = VGroup(*[Dot(point=daughter_nucleus_2.get_center() + 0.15 * RIGHT).set_color(RED) for _ in range(4)])
        daughter_cell_2.add(daughter_nucleus_2)

        self.play(Transform(parent_cell, VGroup(daughter_cell_1, daughter_cell_2)),
                  Transform(parent_nucleus, VGroup(daughter_nucleus_1, daughter_nucleus_2)),
                  Transform(chromosomes, VGroup(daughter_chromosomes_1, daughter_chromosomes_2)),
                  FadeOut(split_arrow))
        self.wait(2)