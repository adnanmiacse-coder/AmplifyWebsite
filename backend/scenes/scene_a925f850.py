from manim import *

config.background_color = BLACK

class Scene(Scene):
    def construct(self):
        title = Text("Mitosis: Simple Cell Division", font_size=40)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        cell = Circle(radius=1.5, color=WHITE)
        nucleus_content = VGroup(
            Circle(radius=0.3, color=RED),
            Square(side_length=0.4, color=BLUE)
        )
        nucleus_content.move_to(cell.get_center())
        cell_group = VGroup(cell, nucleus_content)

        self.play(Create(cell))
        self.play(FadeIn(nucleus_content, scale=0.5))
        self.wait(1)

        chromosomes = VGroup()
        for i in range(2):
            c = Circle(radius=0.15, color=RED).copy()
            s = Square(side_length=0.3, color=BLUE).copy()
            c.move_to(cell.get_center() + (i - 0.5) * RIGHT * 1.5)
            s.move_to(cell.get_center() + (i - 0.5) * RIGHT * 1.5)
            v = VGroup(c, s)
            chromosomes.add(v)

        self.play(Transform(nucleus_content, chromosomes))
        self.wait(1)

        split_chromosomes = VGroup()
        for i in range(len(chromosomes)):
            c1 = chromosomes[i][0].copy().shift(LEFT * 0.5)
            c2 = chromosomes[i][0].copy().shift(RIGHT * 0.5)
            s1 = chromosomes[i][1].copy().shift(LEFT * 0.5)
            s2 = chromosomes[i][1].copy().shift(RIGHT * 0.5)
            split_chromosomes.add(VGroup(c1, s1), VGroup(c2, s2))

        self.play(Transform(chromosomes, split_chromosomes))
        self.wait(1)

        daughter_cell_1 = Circle(radius=1.5, color=WHITE).shift(LEFT * 1.8)
        daughter_cell_2 = Circle(radius=1.5, color=WHITE).shift(RIGHT * 1.8)

        self.play(
            VGroup(cell, chromosomes).animate.scale(0.5).shift(LEFT * 1.8),
            Create(daughter_cell_1)
        )
        self.play(
            VGroup(cell, chromosomes).animate.scale(0.5).shift(RIGHT * 1.8),
            Create(daughter_cell_2)
        )
        
        final_chromosomes_1 = VGroup()
        for i in range(len(chromosomes) // 2):
            final_chromosomes_1.add(chromosomes[i].copy().move_to(daughter_cell_1.get_center()))
        
        final_chromosomes_2 = VGroup()
        for i in range(len(chromosomes) // 2, len(chromosomes)):
            final_chromosomes_2.add(chromosomes[i].copy().move_to(daughter_cell_2.get_center()))

        self.play(Transform(chromosomes[:len(chromosomes)//2], final_chromosomes_1))
        self.play(Transform(chromosomes[len(chromosomes)//2:], final_chromosomes_2))
        self.wait(2)

        self.play(FadeOut(VGroup(daughter_cell_1, daughter_cell_2, chromosomes)))
        self.wait(2)