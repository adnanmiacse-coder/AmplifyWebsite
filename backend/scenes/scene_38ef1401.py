from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis", font_size=72)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        parent_cell = Circle(radius=1, color=WHITE)
        parent_label = Text("Parent Cell", font_size=24).next_to(parent_cell, DOWN)
        group1 = VGroup(parent_cell, parent_label)
        self.play(Create(group1))
        self.wait(1)

        chromosome_1 = Square(side_length=0.2, color=RED).move_to(parent_cell.get_center() + LEFT * 0.3)
        chromosome_2 = Square(side_length=0.2, color=BLUE).move_to(parent_cell.get_center() + RIGHT * 0.3)
        chromosomes = VGroup(chromosome_1, chromosome_2)
        self.play(Create(chromosomes))
        self.wait(1)

        # DNA Replication
        chr1_dup = chromosome_1.copy().scale(0.5).move_to(chromosome_1.get_center() + UP * 0.2)
        chr2_dup = chromosome_2.copy().scale(0.5).move_to(chromosome_2.get_center() + UP * 0.2)
        duplicated_chromosomes = VGroup(chr1_dup, chr2_dup)
        self.play(Transform(chromosome_1, chr1_dup), Transform(chromosome_2, chr2_dup))
        self.wait(1.5)

        # Nuclear Envelope Breakdown (Simplified)
        self.play(FadeOut(parent_label))
        self.play(parent_cell.animate.scale(0.5))
        self.wait(0.5)

        # Chromosomes align at metaphase plate
        aligned_chr1 = chromosome_1.copy().move_to(ORIGIN + LEFT * 1)
        aligned_chr2 = chromosome_2.copy().move_to(ORIGIN + RIGHT * 1)
        aligned_group = VGroup(aligned_chr1, aligned_chr2)
        self.play(Transform(chromosome_1, aligned_chr1), Transform(chromosome_2, aligned_chr2))
        self.wait(1)

        # Sister chromatids separate
        sep_chr1_a = chromosome_1.copy().move_to(LEFT * 1.5)
        sep_chr1_b = chromosome_1.copy().move_to(LEFT * 0.5).set_color(YELLOW)
        sep_chr2_a = chromosome_2.copy().move_to(RIGHT * 1.5)
        sep_chr2_b = chromosome_2.copy().move_to(RIGHT * 0.5).set_color(GREEN)

        arrow1 = Arrow(chromosome_1.get_center(), LEFT * 1.5, buff=0)
        arrow2 = Arrow(chromosome_1.get_center(), LEFT * 0.5, buff=0)
        arrow3 = Arrow(chromosome_2.get_center(), RIGHT * 1.5, buff=0)
        arrow4 = Arrow(chromosome_2.get_center(), RIGHT * 0.5, buff=0)

        self.play(
            Transform(chromosome_1, sep_chr1_a),
            Transform(chromosome_2, sep_chr2_a),
            Create(arrow1),
            Create(arrow3)
        )
        self.wait(1)
        self.play(
            FadeIn(sep_chr1_b, shift=LEFT*0.5),
            FadeIn(sep_chr2_b, shift=RIGHT*0.5),
            Transform(arrow1, arrow2),
            Transform(arrow3, arrow4)
        )
        self.wait(1)
        self.play(FadeOut(VGroup(arrow1, arrow2, arrow3, arrow4)))

        # Two daughter cells form
        daughter_cell_1 = Circle(radius=0.7, color=WHITE).move_to(LEFT * 1.5)
        daughter_cell_2 = Circle(radius=0.7, color=WHITE).move_to(RIGHT * 1.5)
        daughter_label_1 = Text("Daughter Cell", font_size=24).next_to(daughter_cell_1, DOWN)
        daughter_label_2 = Text("Daughter Cell", font_size=24).next_to(daughter_cell_2, DOWN)

        daughter_group_1 = VGroup(daughter_cell_1, daughter_label_1, sep_chr1_a, sep_chr1_b)
        daughter_group_2 = VGroup(daughter_cell_2, daughter_label_2, sep_chr2_a, sep_chr2_b)

        self.play(
            Transform(parent_cell, daughter_cell_1),
            Transform(VGroup(chromosome_1, chr1_dup), daughter_group_1),
            Transform(VGroup(chromosome_2, chr2_dup), daughter_group_2)
        )
        self.play(FadeOut(VGroup(parent_cell)), FadeOut(VGroup(chromosome_1)), FadeOut(VGroup(chromosome_2)))
        self.play(Create(daughter_group_1), Create(daughter_group_2))
        self.wait(2)