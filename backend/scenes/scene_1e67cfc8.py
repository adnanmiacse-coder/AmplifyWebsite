from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        cell = Circle(radius=1, color=WHITE)
        nucleus = Circle(radius=0.4, color=BLUE)
        cell.add(nucleus)
        self.play(FadeIn(cell))
        self.wait(1)

        dna_strands = VGroup(
            Line(cell.get_center() + DOWN * 0.3, cell.get_center() + UP * 0.3, color=RED),
            Line(cell.get_center() + UP * 0.3, cell.get_center() + DOWN * 0.3, color=RED)
        )
        nucleus.add(dna_strands[0], dna_strands[1])
        self.play(Create(dna_strands))
        self.wait(1)

        arrow1 = Arrow(start=cell.get_right() + RIGHT, end=cell.get_right() + RIGHT * 2, buff=0.2)
        text1 = Text("Replication", font_size=24).next_to(arrow1, RIGHT)
        self.play(Create(arrow1), Write(text1))
        self.wait(1)

        duplicated_dna1 = Line(cell.get_center() + DOWN * 0.3, cell.get_center() + UP * 0.3, color=RED).copy()
        duplicated_dna2 = Line(cell.get_center() + DOWN * 0.3, cell.get_center() + UP * 0.3, color=RED).copy()
        nucleus.add(duplicated_dna1, duplicated_dna2)
        self.play(Transform(dna_strands[0], duplicated_dna1), Transform(dna_strands[1], duplicated_dna2))
        self.wait(1)
        self.play(FadeOut(arrow1, text1))

        arrow2 = Arrow(start=cell.get_center(), end=cell.get_center() + RIGHT * 2.5, buff=0.2)
        text2 = Text("Condensation & Alignment", font_size=24).next_to(arrow2, RIGHT)
        self.play(Create(arrow2), Write(text2))
        self.wait(1)

        chromosome1 = Line(cell.get_center() + LEFT * 0.5, cell.get_center() + RIGHT * 0.5, color=RED)
        chromosome2 = Line(cell.get_center() + LEFT * 0.5, cell.get_center() + RIGHT * 0.5, color=RED)
        chromosome1.rotate(PI/2, about_point=cell.get_center())
        chromosome2.rotate(-PI/2, about_point=cell.get_center())
        nucleus.remove(duplicated_dna1, duplicated_dna2)
        nucleus.add(chromosome1, chromosome2)
        self.play(Transform(VGroup(duplicated_dna1, duplicated_dna2), VGroup(chromosome1, chromosome2)))
        self.wait(1)
        self.play(FadeOut(arrow2, text2))

        arrow3 = Arrow(start=cell.get_center()+RIGHT, end=cell.get_center()+RIGHT*3, buff=0.2)
        text3 = Text("Separation", font_size=24).next_to(arrow3, RIGHT)
        self.play(Create(arrow3), Write(text3))
        self.wait(1)

        split_chromosome1_part1 = Line(cell.get_center() + LEFT * 0.5, cell.get_center(), color=RED)
        split_chromosome1_part2 = Line(cell.get_center(), cell.get_center() + RIGHT * 0.5, color=RED)
        split_chromosome2_part1 = Line(cell.get_center() + LEFT * 0.5, cell.get_center(), color=RED)
        split_chromosome2_part2 = Line(cell.get_center(), cell.get_center() + RIGHT * 0.5, color=RED)

        split_chromosome1_part1.rotate(PI/2, about_point=cell.get_center())
        split_chromosome1_part2.rotate(PI/2, about_point=cell.get_center())
        split_chromosome2_part1.rotate(-PI/2, about_point=cell.get_center())
        split_chromosome2_part2.rotate(-PI/2, about_point=cell.get_center())

        nucleus.remove(chromosome1, chromosome2)
        nucleus.add(split_chromosome1_part1, split_chromosome1_part2, split_chromosome2_part1, split_chromosome2_part2)

        chromosomes_group1 = VGroup(split_chromosome1_part1, split_chromosome1_part2)
        chromosomes_group2 = VGroup(split_chromosome2_part1, split_chromosome2_part2)
        
        transformed_chromosomes = VGroup(chromosomes_group1, chromosomes_group2)
        original_chromosomes = VGroup(chromosome1, chromosome2)

        self.play(
            Transform(original_chromosomes, transformed_chromosomes)
        )

        self.play(
            FadeOut(arrow3), FadeOut(text3)
        )
        self.wait(1)

        cell_split_line = Line(cell.get_center() + LEFT*0.7, cell.get_center() + RIGHT*0.7, color=WHITE)
        self.play(Create(cell_split_line))
        self.wait(1)

        daughter_cell1 = Circle(radius=1, color=WHITE).shift(LEFT*1.2)
        daughter_nucleus1 = Circle(radius=0.4, color=BLUE).move_to(daughter_cell1.get_center())
        daughter_cell1.add(daughter_nucleus1)
        daughter_nucleus1.add(Line(daughter_cell1.get_center() + DOWN * 0.3, daughter_cell1.get_center() + UP *