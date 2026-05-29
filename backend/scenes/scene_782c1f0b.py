from manim import *

config.background_color = BLACK

class Scene(Scene):
    def construct(self):
        title = Text("Mitosis: Cell Division", color=WHITE)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        parent_cell = Circle(radius=1, color=BLUE)
        parent_nucleus = Circle(radius=0.3, color=WHITE)
        parent_cell.add(parent_nucleus)

        self.play(Create(parent_cell))
        self.wait(1)

        chromosomes = VGroup(
            Line(0.3*LEFT, 0.3*RIGHT, color=RED),
            Line(0.3*LEFT, 0.3*RIGHT, color=RED),
            Line(0.3*UP, 0.3*DOWN, color=RED),
            Line(0.3*UP, 0.3*DOWN, color=RED)
        ).move_to(parent_nucleus)

        self.play(parent_nucleus.animate.scale(1.5))
        self.play(Create(chromosomes))
        self.wait(1)

        duplicated_chromosomes = VGroup(
            Line(0.3*LEFT, 0.3*RIGHT, color=RED),
            Line(0.3*LEFT, 0.3*RIGHT, color=RED),
            Line(0.3*UP, 0.3*DOWN, color=RED),
            Line(0.3*UP, 0.3*DOWN, color=RED)
        ).move_to(parent_nucleus)

        self.play(Transform(chromosomes, duplicated_chromosomes.copy().shift(0.2*RIGHT)))
        self.play(Transform(chromosomes, duplicated_chromosomes.copy().shift(0.2*LEFT)))
        self.wait(1)

        self.play(FadeOut(chromosomes))

        daughter_cell_1_nucleus = Circle(radius=0.3, color=WHITE)
        daughter_cell_2_nucleus = Circle(radius=0.3, color=WHITE)

        daughter_cell_1 = Circle(radius=1, color=GREEN)
        daughter_cell_2 = Circle(radius=1, color=GREEN)

        daughter_cell_1.add(daughter_cell_1_nucleus.move_to(parent_cell.get_center() + 0.7*LEFT))
        daughter_cell_2.add(daughter_cell_2_nucleus.move_to(parent_cell.get_center() + 0.7*RIGHT))

        self.play(
            parent_cell.animate.scale(0.5).shift(0.7*LEFT),
            daughter_cell_1.animate.scale(0.5).shift(0.7*LEFT),
            FadeIn(daughter_cell_1)
        )
        self.play(
            parent_cell.animate.scale(0.5).shift(1.4*RIGHT),
            daughter_cell_2.animate.scale(0.5).shift(0.7*RIGHT),
            FadeIn(daughter_cell_2)
        )

        self.play(FadeOut(parent_cell))
        self.wait(2)