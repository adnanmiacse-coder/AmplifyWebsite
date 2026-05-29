from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(title.animate.to_edge(UP))

        cell = Circle(radius=1, color=WHITE)
        nucleus = Circle(radius=0.3, color=BLUE)
        cell.add(nucleus)
        self.play(FadeIn(cell))
        self.wait(1)

        chromosome1 = Line(LEFT*0.2, RIGHT*0.2, color=YELLOW)
        chromosome1.move_to([-0.5, 0, 0])
        chromosome2 = Line(LEFT*0.2, RIGHT*0.2, color=RED)
        chromosome2.move_to([0.5, 0, 0])
        nucleus.add(chromosome1, chromosome2)
        self.play(FadeIn(chromosome1), FadeIn(chromosome2))
        self.wait(1)

        chromatid1_copy = chromosome1.copy()
        chromatid1_copy.shift(RIGHT*0.1)
        chromatid2_copy = chromosome2.copy()
        chromatid2_copy.shift(LEFT*0.1)

        self.play(
            chromosome1.animate.shift(LEFT*0.2),
            chromosome2.animate.shift(RIGHT*0.2)
        )
        self.play(
            chromatid1_copy.animate.move_to(chromosome1.get_center() + DOWN*0.1),
            chromatid2_copy.animate.move_to(chromosome2.get_center() + UP*0.1),
            FadeIn(chromatid1_copy),
            FadeIn(chromatid2_copy)
        )
        self.wait(1)

        split_chromosome1 = Line(LEFT*0.2, RIGHT*0.2, color=YELLOW)
        split_chromosome1.move_to([-0.7, 0, 0])
        split_chromosome1_copy_new = Line(LEFT*0.2, RIGHT*0.2, color=YELLOW)
        split_chromosome1_copy_new.move_to([-0.3, 0, 0])

        split_chromosome2 = Line(LEFT*0.2, RIGHT*0.2, color=RED)
        split_chromosome2.move_to([0.7, 0, 0])
        split_chromosome2_copy_new = Line(LEFT*0.2, RIGHT*0.2, color=RED)
        split_chromosome2_copy_new.move_to([0.3, 0, 0])

        self.play(
            FadeOut(chromosome1),
            FadeOut(chromosome2),
            FadeOut(chromatid1_copy),
            FadeOut(chromatid2_copy),
            FadeIn(split_chromosome1),
            FadeIn(split_chromosome1_copy_new),
            FadeIn(split_chromosome2),
            FadeIn(split_chromosome2_copy_new)
        )
        self.wait(1)

        self.play(
            self.camera.frame.animate.scale(0.8).move_to(LEFT*1.5),
            split_chromosome1.animate.next_to(self.camera.frame, RIGHT, buff=0.5),
            split_chromosome1_copy_new.animate.next_to(self.camera.frame, RIGHT, buff=0.5),
            split_chromosome2.animate.next_to(self.camera.frame, LEFT, buff=0.5),
            split_chromosome2_copy_new.animate.next_to(self.camera.frame, LEFT, buff=0.5),
        )

        new_cell_nucleus1 = Circle(radius=0.3, color=BLUE)
        new_cell_nucleus1.move_to([-1.5, -0.5, 0])
        new_cell_nucleus2 = Circle(radius=0.3, color=BLUE)
        new_cell_nucleus2.move_to([1.5, -0.5, 0])

        new_cell1 = Circle(radius=1, color=WHITE)
        new_cell1.move_to([-1.5, -1.5, 0])
        new_cell1.add(new_cell_nucleus1)
        new_cell1.add(split_chromosome1, split_chromosome1_copy_new)

        new_cell2 = Circle(radius=1, color=WHITE)
        new_cell2.move_to([1.5, -1.5, 0])
        new_cell2.add(new_cell_nucleus2)
        new_cell2.add(split_chromosome2, split_chromosome2_copy_new)

        self.play(
            cell.animate.move_to(new_cell1.get_center()).scale(0.7),
            FadeIn(new_cell2)
        )
        self.wait(2)