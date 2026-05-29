from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: The Cell's Dance", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        cell_circle = Circle(radius=1.5, color=WHITE)
        cell_text = Text("Parent Cell", font_size=24).next_to(cell_circle, DOWN)
        parent_cell = VGroup(cell_circle, cell_text)
        self.play(Create(parent_cell))
        self.wait(1)

        chromosomes_text = MathTex("2n Chromosomes", font_size=36).move_to(cell_circle.get_center() + UP*0.5)
        self.play(Write(chromosomes_text))
        self.wait(1)

        # Prophase
        prophase_text = Text("Prophase", font_size=30).to_edge(UP)
        chromosomes = VGroup(*[Circle(radius=0.1, color=RED).move_to(cell_circle.get_center() + UP*0.5 + RIGHT*i*0.2) for i in range(-2, 3)])
        self.play(FadeOut(cell_text), FadeOut(chromosomes_text), Write(prophase_text))
        self.play(Create(chromosomes))
        self.wait(1)

        # Metaphase
        metaphase_text = Text("Metaphase", font_size=30).to_edge(UP)
        metaphase_chromosomes = VGroup(*[c.copy().move_to(cell_circle.get_center() + RIGHT*i*0.3) for i, c in enumerate(chromosomes)])
        self.play(FadeOut(prophase_text), Transform(chromosomes, metaphase_chromosomes), Write(metaphase_text))
        self.wait(1)

        # Anaphase
        anaphase_text = Text("Anaphase", font_size=30).to_edge(UP)
        anaphase_chromosomes_left = VGroup(*[c.copy().move_to(cell_circle.get_center() + LEFT*2 + i*0.2) for i, c in enumerate(chromosomes)])
        anaphase_chromosomes_right = VGroup(*[c.copy().move_to(cell_circle.get_center() + RIGHT*2 + i*0.2) for i, c in enumerate(chromosomes)])
        split_arrow_left = Arrow(cell_circle.get_center(), anaphase_chromosomes_left.get_center(), buff=0)
        split_arrow_right = Arrow(cell_circle.get_center(), anaphase_chromosomes_right.get_center(), buff=0)
        self.play(FadeOut(metaphase_text), Transform(chromosomes, VGroup(anaphase_chromosomes_left, anaphase_chromosomes_right)), Write(anaphase_text))
        self.play(Create(split_arrow_left), Create(split_arrow_right))
        self.wait(1)
        self.play(FadeOut(split_arrow_left), FadeOut(split_arrow_right))

        # Telophase & Cytokinesis
        telophase_text = Text("Telophase & Cytokinesis", font_size=30).to_edge(UP)
        daughter_cell_1 = cell_circle.copy().scale(0.7).move_to(cell_circle.get_center() + LEFT * 1)
        daughter_cell_2 = cell_circle.copy().scale(0.7).move_to(cell_circle.get_center() + RIGHT * 1)
        daughter_text_1 = Text("Daughter Cell", font_size=20).next_to(daughter_cell_1, DOWN)
        daughter_text_2 = Text("Daughter Cell", font_size=20).next_to(daughter_cell_2, DOWN)
        daughter_cells = VGroup(daughter_cell_1, daughter_cell_2, daughter_text_1, daughter_text_2)
        self.play(FadeOut(anaphase_text), FadeOut(chromosomes), Write(telophase_text))
        self.play(FadeOut(cell_circle), FadeOut(cell_text))
        self.play(Create(daughter_cells))
        self.wait(1)

        final_text = Text("Two identical daughter cells!", font_size=36).move_to(UP*2)
        self.play(Write(final_text))
        self.wait(2)
        self.play(*[FadeOut(mob) for mob in self.mobjects])
        self.wait(1)