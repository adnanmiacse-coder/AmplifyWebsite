from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        parent_cell = Circle(radius=1, color=WHITE)
        parent_nucleus = Circle(radius=0.3, color=BLUE)
        parent_cell.add(parent_nucleus)
        self.play(Create(parent_cell))
        self.wait(0.5)

        chromosomes = VGroup(*[Square(side_length=0.2, color=RED).move_to(parent_nucleus.get_center() + 0.2 * RIGHT * i) for i in range(4)])
        self.play(Create(chromosomes))
        self.wait(1)

        chromosomes_replicated = VGroup(
            *[Square(side_length=0.2, color=RED).move_to(parent_nucleus.get_center() + 0.3 * RIGHT * i) for i in range(4)],
            *[Square(side_length=0.2, color=RED).move_to(parent_nucleus.get_center() + 0.3 * LEFT * i) for i in range(4)]
        )
        self.play(Transform(chromosomes, chromosomes_replicated))
        self.wait(1)

        cell_division_line = Line(parent_cell.get_left(), parent_cell.get_right(), color=WHITE)
        self.play(Create(cell_division_line))
        self.wait(1)

        daughter_cell1 = Circle(radius=1, color=WHITE).shift(LEFT * 1.5)
        daughter_nucleus1 = Circle(radius=0.3, color=BLUE).move_to(daughter_cell1.get_center())
        daughter_chromosomes1 = VGroup(*[Square(side_length=0.2, color=RED).move_to(daughter_nucleus1.get_center() + 0.2 * RIGHT * i) for i in range(4)])
        daughter_cell1.add(daughter_nucleus1)
        daughter_cell1.add(daughter_chromosomes1)

        daughter_cell2 = Circle(radius=1, color=WHITE).shift(RIGHT * 1.5)
        daughter_nucleus2 = Circle(radius=0.3, color=BLUE).move_to(daughter_cell2.get_center())
        daughter_chromosomes2 = VGroup(*[Square(side_length=0.2, color=RED).move_to(daughter_nucleus2.get_center() + 0.2 * LEFT * i) for i in range(4)])
        daughter_cell2.add(daughter_nucleus2)
        daughter_cell2.add(daughter_chromosomes2)

        self.play(Transform(parent_cell, VGroup(daughter_cell1, daughter_cell2)))
        self.wait(1)

        self.wait(2)