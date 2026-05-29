from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        cell = Circle(radius=1.5, color=WHITE)
        nucleus = Circle(radius=0.5, color=BLUE)
        chromosomes = VGroup(*[
            Line(start=nucleus.get_center() + UP*0.05, end=nucleus.get_center() + DOWN*0.05, color=RED).rotate(angle, about_point=nucleus.get_center())
            for angle in [0, PI/4, PI/2, 3*PI/4]
        ])
        cell_group = VGroup(cell, nucleus, chromosomes)

        self.play(FadeIn(cell_group))
        self.wait(1)

        mitosis_text = Text("Mitosis", font_size=36).next_to(title, DOWN)
        self.play(Write(mitosis_text))
        self.wait(1)

        # Prophase
        prophase_text = Text("Prophase", font_size=24).to_edge(LEFT)
        self.play(Write(prophase_text))
        self.play(chromosomes.animate.scale(1.2))
        self.wait(1)
        self.play(FadeOut(prophase_text))

        # Metaphase
        metaphase_text = Text("Metaphase", font_size=24).to_edge(LEFT)
        self.play(Write(metaphase_text))
        self.play(chromosomes.animate.arrange(RIGHT, buff=0.5))
        self.wait(1)
        self.play(FadeOut(metaphase_text))

        # Anaphase
        anaphase_text = Text("Anaphase", font_size=24).to_edge(LEFT)
        self.play(Write(anaphase_text))
        split_chromosomes = VGroup()
        for chrom in chromosomes:
            new_chrom = Line(chrom.get_start(), chrom.get_end(), color=RED)
            split_chromosomes.add(new_chrom)
        self.play(Transform(chromosomes, split_chromosomes))
        self.play(chromosomes.animate.center())
        self.play(chromosomes.animate.shift(LEFT*0.7), chromosomes[2:].animate.shift(RIGHT*0.7))
        self.wait(1)
        self.play(FadeOut(anaphase_text))

        # Telophase and Cytokinesis
        telophase_text = Text("Telophase & Cytokinesis", font_size=24).to_edge(LEFT)
        self.play(Write(telophase_text))
        self.play(FadeOut(nucleus), FadeOut(chromosomes))
        new_cell1 = Circle(radius=1, color=WHITE).shift(LEFT*1)
        new_cell2 = Circle(radius=1, color=WHITE).shift(RIGHT*1)
        self.play(FadeIn(new_cell1), FadeIn(new_cell2))
        self.wait(1)
        self.play(FadeOut(telophase_text))

        self.play(FadeOut(cell_group), FadeOut(mitosis_text), FadeOut(title))
        self.wait(2)