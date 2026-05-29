from manim import *

config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        title = Text("Mitosis: Cell Division", font_size=48)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        parent_cell = Circle(radius=1, color=WHITE)
        parent_nucleus = Circle(radius=0.3, color=BLUE)
        parent_cell.add(parent_nucleus)
        parent_label = Text("Parent Cell", font_size=24).next_to(parent_cell, DOWN)

        self.play(Create(parent_cell), Write(parent_label))
        self.wait(1)

        # Chromosome condensation
        chromosome1 = Square(side_length=0.2, color=RED)
        chromosome2 = Square(side_length=0.2, color=YELLOW)
        VGroup(chromosome1, chromosome2).arrange(RIGHT, buff=0.3)
        chromosome1.move_to(parent_nucleus.get_center())
        chromosome2.move_to(parent_nucleus.get_center())
        
        self.play(Transform(parent_nucleus, VGroup(chromosome1, chromosome2)), 
                  FadeOut(parent_label))
        self.wait(1)

        # Chromosome alignment
        aligned_chromosomes = VGroup(chromosome1.copy().set_color(RED), 
                                     chromosome2.copy().set_color(YELLOW))
        aligned_chromosomes.arrange(RIGHT, buff=0.5).move_to(ORIGIN)
        
        self.play(Transform(parent_cell, Circle(radius=1.2, color=WHITE)),
                  Transform(VGroup(chromosome1, chromosome2), aligned_chromosomes))
        self.wait(1)
        
        # Sister chromatids separate
        split_chromosome1a = Square(side_length=0.2, color=RED).move_to(aligned_chromosomes[0].get_center() + LEFT*0.3)
        split_chromosome1b = Square(side_length=0.2, color=RED).move_to(aligned_chromosomes[0].get_center() + RIGHT*0.3)
        split_chromosome2a = Square(side_length=0.2, color=YELLOW).move_to(aligned_chromosomes[1].get_center() + LEFT*0.3)
        split_chromosome2b = Square(side_length=0.2, color=YELLOW).move_to(aligned_chromosomes[1].get_center() + RIGHT*0.3)

        self.play(Transform(aligned_chromosomes[0], VGroup(split_chromosome1a, split_chromosome1b)),
                  Transform(aligned_chromosomes[1], VGroup(split_chromosome2a, split_chromosome2b)))
        self.wait(1)
        
        # New cells form
        new_cell1 = Circle(radius=1, color=WHITE).set_fill(BLACK, opacity=1).move_to(LEFT*2)
        new_nucleus1 = Circle(radius=0.3, color=BLUE).move_to(new_cell1.get_center())
        new_cell1.add(new_nucleus1)
        new_cell1_chromosomes = VGroup(Square(side_length=0.2, color=RED).move_to(new_nucleus1.get_center()),
                                       Square(side_length=0.2, color=YELLOW).move_to(new_nucleus1.get_center()))
        new_cell1.add(new_cell1_chromosomes)

        new_cell2 = Circle(radius=1, color=WHITE).set_fill(BLACK, opacity=1).move_to(RIGHT*2)
        new_nucleus2 = Circle(radius=0.3, color=BLUE).move_to(new_cell2.get_center())
        new_cell2.add(new_nucleus2)
        new_cell2_chromosomes = VGroup(Square(side_length=0.2, color=RED).move_to(new_nucleus2.get_center()),
                                       Square(side_length=0.2, color=YELLOW).move_to(new_nucleus2.get_center()))
        new_cell2.add(new_cell2_chromosomes)
        
        self.play(Transform(parent_cell, VGroup(new_cell1, new_cell2)),
                  Transform(VGroup(split_chromosome1a, split_chromosome1b, split_chromosome2a, split_chromosome2b), 
                            VGroup(new_cell1_chromosomes, new_cell2_chromosomes)))
        
        self.wait(2)