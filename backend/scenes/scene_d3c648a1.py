from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        parent_cell_text = Text("Parent Cell", font_size=30).to_edge(UP)
        parent_nucleus = Circle(radius=1, color=WHITE).move_to(UP*1.5)
        parent_chromosomes = VGroup(
            Line(LEFT*0.2, RIGHT*0.2, color=RED, stroke_width=4),
            Line(LEFT*0.2, RIGHT*0.2, color=BLUE, stroke_width=4)
        ).move_to(parent_nucleus.get_center())

        self.play(Create(parent_nucleus), Write(parent_nucleus_text))
        self.play(Create(parent_chromosomes))
        self.wait(1)

        mitosis_text = Text("Mitosis", font_size=40).next_to(parent_cell_text, DOWN, buff=0.5)
        self.play(Write(mitosis_text))
        self.wait(1)

        split_chromosomes = VGroup(
            Line(LEFT*0.2, RIGHT*0.2, color=RED, stroke_width=4).rotate(PI/2),
            Line(LEFT*0.2, RIGHT*0.2, color=BLUE, stroke_width=4).rotate(PI/2)
        ).scale(0.7).move_to(UP*0.5)

        self.play(Transform(parent_chromosomes, split_chromosomes))
        self.wait(1)

        new_cell_text = Text("Daughter Cells", font_size=30).next_to(mitosis_text, DOWN, buff=1.5)
        daughter_nucleus1 = Circle(radius=0.7, color=WHITE).move_to(LEFT*2 + DOWN*1.5)
        daughter_nucleus2 = Circle(radius=0.7, color=WHITE).move_to(RIGHT*2 + DOWN*1.5)
        daughter_chromosomes1 = VGroup(
            Line(LEFT*0.2, RIGHT*0.2, color=RED, stroke_width=4).rotate(PI/2),
            Line(LEFT*0.2, RIGHT*0.2, color=BLUE, stroke_width=4).rotate(PI/2)
        ).scale(0.7).move_to(daughter_nucleus1.get_center())
        daughter_chromosomes2 = VGroup(
            Line(LEFT*0.2, RIGHT*0.2, color=RED, stroke_width=4).rotate(PI/2),
            Line(LEFT*0.2, RIGHT*0.2, color=BLUE, stroke_width=4).rotate(PI/2)
        ).scale(0.7).move_to(daughter_nucleus2.get_center())


        self.play(
            Transform(parent_nucleus, daughter_nucleus1),
            Transform(parent_chromosomes, daughter_chromosomes1),
            FadeIn(daughter_nucleus2),
            FadeIn(daughter_chromosomes2),
            Write(new_cell_text.move_to(DOWN*2.5))
        )
        self.wait(2)