from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        parent_cell_label = Text("Parent Cell", font_size=24).to_edge(UP)
        parent_circle = Circle(radius=1.5, color=WHITE)
        parent_group = VGroup(parent_circle, parent_cell_label)
        self.play(Create(parent_group))
        self.wait(1)

        chromosomes_label = Text("Chromosomes", font_size=24).next_to(parent_circle, DOWN)
        chromosomes = VGroup(
            Line(UP*0.3, DOWN*0.3, color=RED),
            Line(UP*0.3, DOWN*0.3, color=BLUE)
        ).scale(0.5).move_to(parent_circle.get_center())
        self.play(Write(chromosomes_label), Create(chromosomes))
        self.wait(1)

        duplicated_chromosomes = VGroup(
            Line(UP*0.3, DOWN*0.3, color=RED).set_x(-0.3),
            Line(UP*0.3, DOWN*0.3, color=RED).set_x(0.3),
            Line(UP*0.3, DOWN*0.3, color=BLUE).set_x(-0.3),
            Line(UP*0.3, DOWN*0.3, color=BLUE).set_x(0.3)
        ).scale(0.5).move_to(parent_circle.get_center())
        
        self.play(Transform(chromosomes, duplicated_chromosomes), FadeOut(chromosomes_label))
        self.wait(1)

        arrow_to_daughters = Arrow(start=parent_circle.get_bottom(), end=parent_circle.get_bottom() + DOWN*1.5, buff=0.1)
        self.play(Create(arrow_to_daughters))
        self.wait(1)

        daughter_cell_label_1 = Text("Daughter Cell 1", font_size=24).to_edge(LEFT)
        daughter_circle_1 = Circle(radius=1, color=WHITE).next_to(daughter_cell_label_1, DOWN)
        daughter_chromosomes_1 = VGroup(
            Line(UP*0.3, DOWN*0.3, color=RED).set_x(-0.3),
            Line(UP*0.3, DOWN*0.3, color=BLUE).set_x(0.3)
        ).scale(0.5).move_to(daughter_circle_1.get_center())
        daughter_group_1 = VGroup(daughter_circle_1, daughter_chromosomes_1, daughter_cell_label_1)

        daughter_cell_label_2 = Text("Daughter Cell 2", font_size=24).to_edge(RIGHT)
        daughter_circle_2 = Circle(radius=1, color=WHITE).next_to(daughter_cell_label_2, DOWN)
        daughter_chromosomes_2 = VGroup(
            Line(UP*0.3, DOWN*0.3, color=RED).set_x(-0.3),
            Line(UP*0.3, DOWN*0.3, color=BLUE).set_x(0.3)
        ).scale(0.5).move_to(daughter_circle_2.get_center())
        daughter_group_2 = VGroup(daughter_circle_2, daughter_chromosomes_2, daughter_cell_label_2)

        self.play(
            FadeOut(parent_group),
            FadeOut(arrow_to_daughters),
            Create(daughter_group_1),
            Create(daughter_group_2)
        )
        self.wait(2)