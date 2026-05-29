from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        cell = Circle(radius=1.5, color=WHITE)
        dna = VGroup(
            Line(cell.get_center() + LEFT * 0.5, cell.get_center() + RIGHT * 0.5, color=RED),
            Line(cell.get_center() + UP * 0.5, cell.get_center() + DOWN * 0.5, color=RED)
        )
        dna.scale(0.3)
        dna.move_to(cell.get_center())

        cell_group = VGroup(cell, dna)
        self.play(Create(cell_group))
        self.wait(1)

        # Prophase
        dna_split = VGroup(
            Line(cell.get_center() + LEFT * 0.5, cell.get_center() + RIGHT * 0.5, color=RED),
            Line(cell.get_center() + UP * 0.5, cell.get_center() + DOWN * 0.5, color=RED)
        )
        dna_split.scale(0.3)
        dna_split.move_to(cell.get_center())
        dna_split[0].set_color(PURE_RED)
        dna_split[1].set_color(PURE_RED)

        self.play(Transform(dna, dna_split))
        self.wait(1)

        # Metaphase
        dna_aligned = VGroup(
            Line(cell.get_center() + LEFT * 0.7, cell.get_center() + RIGHT * 0.7, color=RED),
            Line(cell.get_center() + UP * 0.7, cell.get_center() + DOWN * 0.7, color=RED)
        )
        dna_aligned.scale(0.3)
        dna_aligned.move_to(cell.get_center())
        dna_aligned[0].rotate(PI/4)
        dna_aligned[1].rotate(PI/4)

        self.play(Transform(dna, dna_aligned))
        self.wait(1)

        # Anaphase
        dna1 = Line(cell.get_center() + LEFT * 0.7, cell.get_center(), color=RED).scale(0.3)
        dna2 = Line(cell.get_center() + RIGHT * 0.7, cell.get_center(), color=RED).scale(0.3)
        dna3 = Line(cell.get_center() + UP * 0.7, cell.get_center(), color=RED).scale(0.3)
        dna4 = Line(cell.get_center() + DOWN * 0.7, cell.get_center(), color=RED).scale(0.3)

        self.play(dna[0].animate.shift(LEFT*0.7), dna[0].animate.shift(UP*0.7))
        self.play(dna[1].animate.shift(RIGHT*0.7), dna[1].animate.shift(DOWN*0.7))
        self.wait(1)

        # Telophase and Cytokinesis
        new_cell1 = Circle(radius=1.0, color=WHITE).shift(LEFT*0.7)
        new_cell2 = Circle(radius=1.0, color=WHITE).shift(RIGHT*0.7)
        new_dna1 = Line(ORIGIN, ORIGIN, color=RED).scale(0.3).move_to(new_cell1.get_center())
        new_dna2 = Line(ORIGIN, ORIGIN, color=RED).scale(0.3).move_to(new_cell2.get_center())

        self.play(FadeOut(cell), FadeOut(dna))
        self.play(Create(new_cell1), Create(new_cell2), FadeIn(new_dna1), FadeIn(new_dna2))
        self.wait(2)
        self.play(FadeOut(new_cell1), FadeOut(new_cell2), FadeOut(new_dna1), FadeOut(new_dna2))

        self.wait(2)