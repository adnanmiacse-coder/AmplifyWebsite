from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis", color=WHITE)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        cell = Circle(radius=1.5, color=WHITE)
        nucleus = Circle(radius=0.5, color=BLUE)
        nucleus.move_to(cell.get_center())
        cell_group = VGroup(cell, nucleus)

        self.play(Create(cell_group))
        self.wait(1)

        chromosomes1 = MathTex("X", color=RED).scale(0.5)
        chromosomes1.move_to(cell.get_center())
        chromosomes2 = MathTex("X", color=RED).scale(0.5)
        chromosomes2.move_to(cell.get_center() + RIGHT*0.2)
        chromosomes = VGroup(chromosomes1, chromosomes2)

        self.play(FadeIn(chromosomes))
        self.wait(1)

        sister_chromatids_arrow = Arrow(chromosomes.get_center(), cell.get_center() + UP*0.5, color=WHITE)
        self.play(GrowArrow(sister_chromatids_arrow))
        self.wait(1)
        self.play(FadeOut(sister_chromatids_arrow))

        duplicated_chromosomes = VGroup(
            MathTex("X", color=RED).scale(0.5).move_to(cell.get_center() - LEFT * 0.3),
            MathTex("X", color=RED).scale(0.5).move_to(cell.get_center() + LEFT * 0.3),
            MathTex("X", color=RED).scale(0.5).move_to(cell.get_center() - RIGHT * 0.3),
            MathTex("X", color=RED).scale(0.5).move_to(cell.get_center() + RIGHT * 0.3)
        )
        self.play(Transform(chromosomes, duplicated_chromosomes))
        self.wait(1)

        split_arrow = Arrow(cell.get_center(), cell.get_center() + DOWN*0.5, color=WHITE)
        self.play(GrowArrow(split_arrow))
        self.wait(1)
        self.play(FadeOut(split_arrow))

        new_cells = VGroup(
            Circle(radius=1, color=WHITE).move_to(cell.get_center() + LEFT*1),
            Circle(radius=1, color=WHITE).move_to(cell.get_center() + RIGHT*1)
        )
        new_nuclei = VGroup(
            Circle(radius=0.3, color=BLUE).move_to(cell.get_center() + LEFT*1),
            Circle(radius=0.3, color=BLUE).move_to(cell.get_center() + RIGHT*1)
        )
        new_cells_group = VGroup(new_cells, new_nuclei)

        final_chromosomes1 = VGroup(
            MathTex("X", color=RED).scale(0.3).move_to(new_cells[0].get_center() - LEFT*0.3),
            MathTex("X", color=RED).scale(0.3).move_to(new_cells[0].get_center() + LEFT*0.3)
        )
        final_chromosomes2 = VGroup(
            MathTex("X", color=RED).scale(0.3).move_to(new_cells[1].get_center() - RIGHT*0.3),
            MathTex("X", color=RED).scale(0.3).move_to(new_cells[1].get_center() + RIGHT*0.3)
        )
        final_chromosomes_group = VGroup(final_chromosomes1, final_chromosomes2)

        self.play(
            FadeOut(cell),
            FadeOut(nucleus),
            FadeOut(chromosomes),
            Create(new_cells_group),
            FadeIn(final_chromosomes_group)
        )
        self.wait(2)