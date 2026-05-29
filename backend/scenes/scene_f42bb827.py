from manim import *

config.background_color = BLACK

class Scene(Scene):
    def construct(self):
        title = Text("Cell Division", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        cell1 = Circle(radius=1, color=WHITE)
        cell1_label = Text("Parent Cell", font_size=24).next_to(cell1, DOWN)
        parent_group = VGroup(cell1, cell1_label)
        self.play(Create(parent_group))
        self.wait(1)

        daughter_cell1 = Circle(radius=0.7, color=BLUE).shift(LEFT*1.5)
        daughter_cell2 = Circle(radius=0.7, color=RED).shift(RIGHT*1.5)
        daughter_label1 = Text("Daughter Cell 1", font_size=24).next_to(daughter_cell1, DOWN)
        daughter_label2 = Text("Daughter Cell 2", font_size=24).next_to(daughter_cell2, DOWN)
        daughter_group = VGroup(daughter_cell1, daughter_label1, daughter_cell2, daughter_label2)

        arrow = Arrow(cell1.get_right(), daughter_cell1.get_left(), buff=0.5)
        arrow2 = Arrow(cell1.get_left(), daughter_cell2.get_right(), buff=0.5)

        self.play(Transform(parent_group, daughter_group),
                  FadeIn(arrow),
                  FadeIn(arrow2))
        self.wait(2)
        self.play(FadeOut(parent_group), FadeOut(arrow), FadeOut(arrow2))

        self.wait(2)