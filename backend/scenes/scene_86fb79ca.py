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
        cell.add_to_back(nucleus)
        self.play(Create(cell), Create(nucleus))

        chromosomes = VGroup(*[Dot(radius=0.05, color=RED) for _ in range(4)])
        chromosomes.arrange(RIGHT, buff=0.2)
        chromosomes.move_to(nucleus.get_center() + UP * 0.7)
        self.play(FadeIn(chromosomes, scale=3))
        self.wait(1)

        self.play(self.camera.frame.animate.scale(0.7).move_to(cell.get_center()))
        self.wait(0.5)

        label_start = Text("Interphase", font_size=24).next_to(cell, DOWN)
        self.play(Write(label_start))
        self.wait(1)
        self.play(FadeOut(label_start))

        prophase = Text("Prophase", font_size=24).next_to(cell, DOWN)
        self.play(Write(prophase))
        self.play(chromosomes.animate.shift(DOWN*0.2))
        self.wait(1)
        self.play(FadeOut(prophase))

        metaphase = Text("Metaphase", font_size=24).next_to(cell, DOWN)
        self.play(Write(metaphase))
        self.play(chromosomes.animate.arrange(RIGHT, buff=0.5).move_to(cell.get_center()))
        self.wait(1)
        self.play(FadeOut(metaphase))

        anaphase = Text("Anaphase", font_size=24).next_to(cell, DOWN)
        self.play(Write(anaphase))
        new_chromosomes = VGroup(*[Dot(radius=0.05, color=RED) for _ in range(4)])
        new_chromosomes.arrange(RIGHT, buff=0.2)
        new_chromosomes.move_to(cell.get_center() + UP * 0.7)
        self.play(
            Transform(chromosomes[0], chromosomes[0].copy().set_color(YELLOW).move_to(cell.get_center() + LEFT*0.6 + UP*0.3)),
            Transform(chromosomes[2], chromosomes[2].copy().set_color(YELLOW).move_to(cell.get_center() + RIGHT*0.6 + UP*0.3)),
            Transform(chromosomes[1], chromosomes[1].copy().set_color(YELLOW).move_to(cell.get_center() + LEFT*0.6 + DOWN*0.3)),
            Transform(chromosomes[3], chromosomes[3].copy().set_color(YELLOW).move_to(cell.get_center() + RIGHT*0.6 + DOWN*0.3))
        )
        self.wait(1)
        self.play(FadeOut(anaphase))

        telophase = Text("Telophase", font_size=24).next_to(cell, DOWN)
        self.play(Write(telophase))
        self.play(
            FadeOut(chromosomes),
            FadeOut(nucleus),
            cell.animate.scale(1.2)
        )
        self.wait(1)
        self.play(FadeOut(telophase))

        self.play(self.camera.frame.animate.scale(1/0.7).move_to(ORIGIN))
        self.play(FadeOut(cell), FadeOut(title))
        self.wait(2)