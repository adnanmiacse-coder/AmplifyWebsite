from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=36).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        parent_cell = Circle(radius=1, color=WHITE).shift(LEFT)
        parent_nucleus = Circle(radius=0.3, color=RED).move_to(parent_cell.get_center())
        parent_dna = Square(side_length=0.2, color=YELLOW).move_to(parent_nucleus.get_center()).rotate(PI/4)

        cell_group = VGroup(parent_cell, parent_nucleus, parent_dna)
        self.play(Create(parent_cell), Create(parent_nucleus), Create(parent_dna))
        self.wait(1)

        dna_replication_text = Text("DNA Replication", font_size=24).next_to(cell_group, DOWN)
        dna_doubled = parent_dna.copy().shift(RIGHT*0.3)
        dna_doubled.set_color(GREEN)
        self.play(Write(dna_replication_text))
        self.play(Transform(parent_dna, VGroup(parent_dna, dna_doubled)))
        self.wait(1)
        self.play(FadeOut(dna_replication_text))

        chromosomes_align = VGroup(parent_dna, dna_doubled).arrange(RIGHT, buff=0.1).move_to(parent_nucleus.get_center())
        self.play(FadeOut(parent_nucleus), FadeIn(chromosomes_align))
        self.wait(1)

        splitting_dna = Arrow(chromosomes_align.get_left(), chromosomes_align.get_left() + LEFT*1.5, buff=0.1, color=WHITE)
        splitting_dna_to = Arrow(chromosomes_align.get_right(), chromosomes_align.get_right() + RIGHT*1.5, buff=0.1, color=WHITE)

        daughter_dna_1 = Square(side_length=0.2, color=YELLOW).rotate(PI/4).shift(LEFT*1.5)
        daughter_dna_2 = Square(side_length=0.2, color=GREEN).rotate(PI/4).shift(RIGHT*1.5)

        self.play(Create(splitting_dna), Create(splitting_dna_to))
        self.play(FadeOut(chromosomes_align), Transform(splitting_dna, daughter_dna_1), Transform(splitting_dna_to, daughter_dna_2))
        self.wait(1)

        daughter_cell_1 = Circle(radius=1, color=WHITE).shift(LEFT*2)
        daughter_cell_2 = Circle(radius=1, color=WHITE).shift(RIGHT*2)

        daughter_nucleus_1 = Circle(radius=0.3, color=RED).move_to(daughter_cell_1.get_center())
        daughter_nucleus_2 = Circle(radius=0.3, color=RED).move_to(daughter_cell_2.get_center())

        self.play(FadeOut(parent_cell), FadeIn(daughter_cell_1), FadeIn(daughter_cell_2))
        self.play(FadeOut(splitting_dna), FadeOut(splitting_dna_to), FadeIn(daughter_nucleus_1), FadeIn(daughter_nucleus_2))
        self.play(Transform(daughter_dna_1, daughter_nucleus_1), Transform(daughter_dna_2, daughter_nucleus_2))
        self.wait(1)

        self.play(FadeOut(title), FadeOut(VGroup(daughter_cell_1, daughter_cell_2, daughter_nucleus_1, daughter_nucleus_2)))
        self.wait(2)