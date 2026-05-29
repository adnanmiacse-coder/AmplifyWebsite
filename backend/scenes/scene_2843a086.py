from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=48).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        cell = Circle(radius=1, color=WHITE)
        nucleus = Circle(radius=0.3, color=BLUE)
        cell.add(nucleus)
        self.play(Create(cell))

        chromosomes = VGroup(*[
            Line(start=(-0.2, 0), end=(0.2, 0), color=RED).move_to(nucleus.get_center()).shift(UP * i * 0.1)
            for i in range(-2, 3)
        ])
        self.play(Write(chromosomes))
        self.wait(1)

        chromosomes_duplicated = VGroup(*[
            Line(start=(-0.2, 0), end=(0.2, 0), color=RED).move_to(nucleus.get_center()).shift(UP * i * 0.1)
            for i in range(-2, 3)
        ])
        chromosomes_duplicated.add(*[
            Line(start=(-0.2, 0), end=(0.2, 0), color=RED).move_to(nucleus.get_center()).shift(DOWN * i * 0.1)
            for i in range(-2, 3)
        ])
        self.play(Transform(chromosomes, chromosomes_duplicated))
        self.wait(1)

        chromosomes_aligned = VGroup(*[
            line.copy().rotate(PI/2).scale(0.5).move_to(ORIGIN)
            for line in chromosomes_duplicated
        ])
        self.play(chromosomes_duplicated.animate.arrange(RIGHT, buff=0.1).move_to(ORIGIN))
        self.wait(1)

        cell_division_lines = VGroup(
            Line(start=(-1, 0), end=(1, 0), color=GREEN).shift(UP * 0.5),
            Line(start=(-1, 0), end=(1, 0), color=GREEN).shift(DOWN * 0.5)
        )
        self.play(Create(cell_division_lines))
        self.wait(1)

        new_cell_1 = Circle(radius=1, color=WHITE).shift(LEFT * 1.5)
        new_cell_2 = Circle(radius=1, color=WHITE).shift(RIGHT * 1.5)
        nucleus_1 = Circle(radius=0.3, color=BLUE).move_to(new_cell_1.get_center())
        nucleus_2 = Circle(radius=0.3, color=BLUE).move_to(new_cell_2.get_center())
        new_cell_1.add(nucleus_1)
        new_cell_2.add(nucleus_2)
        
        self.play(
            FadeOut(chromosomes),
            FadeOut(cell_division_lines),
            Transform(cell, VGroup(new_cell_1, new_cell_2))
        )
        self.wait(2)