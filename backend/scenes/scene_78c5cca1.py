from manim import *

config.background_color = BLACK

class Scene(Scene):
    def construct(self):
        title = Text("Cell Division", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        parent_cell = Circle(radius=1, color=WHITE)
        parent_cell_label = Text("Parent Cell", font_size=24).next_to(parent_cell, DOWN)
        parent_group = VGroup(parent_cell, parent_cell_label)

        self.play(FadeIn(parent_group))
        self.wait(1)

        daughter_cell_1 = Circle(radius=0.7, color=BLUE).shift(LEFT * 1)
        daughter_cell_2 = Circle(radius=0.7, color=RED).shift(RIGHT * 1)
        daughter_label_1 = Text("Daughter Cell", font_size=20).next_to(daughter_cell_1, DOWN)
        daughter_label_2 = Text("Daughter Cell", font_size=20).next_to(daughter_cell_2, DOWN)
        daughter_group = VGroup(daughter_cell_1, daughter_label_1, daughter_cell_2, daughter_label_2)

        division_arrow = Arrow(start=LEFT, end=RIGHT, color=YELLOW)
        division_text = Text("Division", font_size=28).next_to(division_arrow, UP)
        division_group = VGroup(division_arrow, division_text)
        division_group.move_to(ORIGIN)

        self.play(Transform(parent_group, division_group))
        self.wait(1)
        self.play(FadeOut(division_group))
        self.play(FadeOut(parent_group), FadeIn(daughter_group))
        self.wait(2)