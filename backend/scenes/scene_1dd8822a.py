from manim import *

config.background_color = BLACK

class Scene(Scene):
    def construct(self):
        title = Text("Cell Structure", font_size=60)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        cell = Circle(radius=2, color=WHITE)
        nucleus = Circle(radius=0.7, color=BLUE)
        dna = Square(side_length=0.5, color=RED)
        dna.next_to(nucleus, DOWN, buff=0.2)

        cell_group = VGroup(cell, nucleus, dna)
        self.play(Create(cell_group))
        self.wait(1)

        mutation_text = Text("Mutation", font_size=36, color=RED)
        mutation_text.next_to(cell, RIGHT, buff=1.5)
        arrow_to_dna = Arrow(start=cell.get_right(), end=dna.get_right(), buff=0.1, color=RED)

        self.play(Write(mutation_text), Create(arrow_to_dna))
        self.wait(2)
        self.play(FadeOut(mutation_text), FadeOut(arrow_to_dna))

        abnormal_growth_text = Text("Abnormal Growth", font_size=36, color=YELLOW)
        abnormal_growth_text.next_to(cell, UP, buff=1.5)
        cell_new = Circle(radius=2.5, color=YELLOW)
        nucleus_new = Circle(radius=0.9, color=BLUE)
        dna_new = Square(side_length=0.7, color=RED)
        dna_new.next_to(nucleus_new, DOWN, buff=0.2)
        cell_group_new = VGroup(cell_new, nucleus_new, dna_new)
        arrow_to_cell = Arrow(start=cell.get_top(), end=cell_group_new.get_top(), buff=0.1, color=YELLOW)

        self.play(Write(abnormal_growth_text), Transform(cell_group, cell_group_new), Create(arrow_to_cell))
        self.wait(2)
        self.play(FadeOut(abnormal_growth_text), FadeOut(arrow_to_cell), FadeOut(cell_group))

        self.wait(2)