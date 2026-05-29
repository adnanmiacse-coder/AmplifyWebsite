from manim import *
config.background_color = BLACK

class Scene(MovingCameraScene):
    def construct(self):
        self.camera.frame.scale(1.5)
        self.camera.frame.shift(DOWN * 0.5)

        # Title Card
        title = Text("Cell Division: From Single to Multicellular Life", color=YELLOW).scale(1.2)
        self.play(Write(title))
        self.wait(2)
        self.play(FadeOut(title))
        self.wait(1)

        # Step 1: The Beginning - Single Cell
        origin_text = Text("Origin of Life (~3.8 Billion Years Ago)", color=WHITE).to_edge(UP)
        self.play(Write(origin_text))
        self.wait(1.5)

        single_cell_proto = Circle(radius=1, color=BLUE, fill_opacity=0.6)
        single_cell_label = Text("Single-celled Organism", color=BLUE).next_to(single_cell_proto, DOWN, buff=0.2)
        self.play(Create(single_cell_proto), Write(single_cell_label))
        self.wait(2)

        # Step 2: Simple Reproduction - Binary Fission
        reproduction_text = Text("Simple Reproduction: Binary Fission", color=WHITE).to_corner(UL)
        self.play(Write(reproduction_text))
        self.wait(1.5)

        arrow1 = Arrow(start=single_cell_proto.get_center() + RIGHT * 1.5,
                       end=single_cell_proto.get_center() + RIGHT * 3,
                       color=GREEN, buff=0.2)
        arrow1_label = Text("Divides", color=GREEN).next_to(arrow1, RIGHT, buff=0.2)
        self.play(GrowArrow(arrow1))
        self.play(Write(arrow1_label))
        self.wait(2)

        cell1 = single_cell_proto.copy().set_color(BLUE).shift(RIGHT * 2.5)
        cell2 = single_cell_proto.copy().set_color(BLUE).shift(LEFT * 2.5)
        cell1_label = Text("Cell 1", color=BLUE).next_to(cell1, DOWN, buff=0.2)
        cell2_label = Text("Cell 2", color=BLUE).next_to(cell2, DOWN, buff=0.2)

        self.play(ReplacementTransform(single_cell_proto, VGroup(cell1, cell2)),
                  FadeOut(single_cell_label),
                  Write(cell1_label), Write(cell2_label))
        self.wait(3)

        # Step 3: The Rise of Multicellularity
        multicellular_text = Text("Evolution towards Multicellular Organisms", color=WHITE).to_edge(UP)
        self.play(FadeOut(origin_text, reproduction_text), Write(multicellular_text))
        self.wait(1.5)

        arrow2 = Arrow(start=cell1.get_center(),
                       end=cell1.get_center() + UP * 2,
                       color=PURPLE, buff=0.2)
        arrow2_label = Text("More Divisions", color=PURPLE).next_to(arrow2, UP, buff=0.2)
        self.play(GrowArrow(arrow2), Write(arrow2_label))
        self.wait(2)

        # Step 4: Mitosis - For Growth and Repair
        mitosis_text = Text("Mitosis: For Growth & Repair", color=WHITE).to_corner(UL)
        self.play(Write(mitosis_text))
        self.wait(1.5)

        # Representing a simplified cell with DNA
        cell_group = VGroup()
        main_cell = Circle(radius=1, color=TEAL, fill_opacity=0.6)
        dna_helix1 = Line(start=main_cell.center + LEFT * 0.5, end=main_cell.center + RIGHT * 0.5, color=RED, stroke_width=4)
        dna_helix2 = Line(start=main_cell.center + LEFT * 0.5, end=main_cell.center + RIGHT * 0.5, color=RED, stroke_width=4).rotate(PI/2, about_point=main_cell.center)
        nucleus = Circle(radius=0.3, color=WHITE, fill_opacity=1).move_to(main_cell.center)
        cell_group.add(main_cell, dna_helix1, dna_helix2, nucleus)
        cell_label = Text("Somatic Cell", color=TEAL).next_to(main_cell, DOWN)
        cell_group.add(cell_label)

        self.play(FadeOut(cell1, cell2, cell1_label, cell2_label),
                  Create(main_cell), Write(cell_label))
        self.wait(1.5)
        self.play(Create(dna_helix1), Create(dna_helix2))
        self.wait(1.5)
        self.play(Create(nucleus))
        self.wait(2)

        # Step 5: DNA Replication and Chromosome Formation
        replication_text = Text("DNA Replication & Chromosome Formation", color=WHITE).to_corner(UR)
        self.play(Write(replication_text))
        self.wait(1.5)

        # Animate chromosome formation
        chromosomes = VGroup()
        # First pair
        chr1a = Line(start=main_cell.center + LEFT * 0.4, end=main_cell.center + LEFT * 0.2, color=RED, stroke_width=4).rotate(PI/4, about_point=main_cell.center)
        chr1b = Line(start=main_cell.center + LEFT * 0.2, end=main_cell.center + LEFT * 0.4, color=RED, stroke_width=4).rotate(-PI/4, about_point=main_cell.center).move_to(main_cell.center)
        chromosomes.add(chr1a, chr1b)
        # Second pair
        chr2a = Line(start=main_cell.center + RIGHT * 0.4, end=main_cell.center + RIGHT * 0.2, color=RED, stroke_width=4).rotate(-PI/4, about_point=main_cell.center)
        chr2b = Line(start=main_cell.center + RIGHT * 0.2, end=main_cell.center + RIGHT * 0.4, color=RED, stroke_width=4).rotate(PI/4, about_point=main_cell.center).move_to(main_cell.center)
        chromosomes.add(chr2a, chr2b)

        self.play(Transform(dna_helix1, chr1a), Transform(dna_helix2, chr1b))
        self.wait(1.5)
        self.play(Create(chr2a), Create(chr2b))
        self.wait(2)

        # Step 6: Division into Two Identical Cells
        division_arrow = Arrow(start=main_cell.get_center(), end=main_cell.get_center() + RIGHT * 2, color=YELLOW, buff=0.2)
        self.play(GrowArrow(division_arrow))
        self.wait(1.5)

        new_cell1 = Circle(radius=1, color=TEAL, fill_opacity=0.6).shift(RIGHT * 2.5)
        new_cell1_label = Text("Daughter Cell 1", color=TEAL).next_to(new_cell1, DOWN, buff=0.2)
        new_cell2 = Circle(radius=1, color=TEAL, fill_opacity=0.6).shift(LEFT * 2.5)
        new_cell2_label = Text("Daughter Cell 2", color=TEAL).next_to(new_cell2, DOWN, buff=0.2)

        # Show chromosomes moving to future poles (simplified)
        grouped_chromosomes1 = VGroup(chr1a.copy(), chr2a.copy()).move_to(new_cell1.center + LEFT * 0.8)
        grouped_chromosomes2 = VGroup(chr1b.copy(), chr2b.copy()).move_to(new_cell2.center + RIGHT*0.8)

        self.play(
            FadeOut(nucleus, dna_helix1, dna_helix2, chr1a, chr1b, chr2a, chr2b, division_arrow, arrow2_label),
            Transform(main_cell, VGroup(new_cell1, new_cell2)),
            Write(VGroup(new_cell1_label, new_cell2_label)),
            FadeIn(grouped_chromosomes1), FadeIn(grouped_chromosomes2)
        )
        self.wait(3)

        # Step 7: Meiosis - For Sexual Reproduction (Brief Mention)
        meiosis_text = Text("Meiosis: For Sexual Reproduction", color=WHITE).to_edge(DOWN, buff=0.5)
        self.play(Write(meiosis_text))
        self.wait(2)
        self.play(FadeOut(grouped_chromosomes1, grouped_chromosomes2, multicellular_text, mitosis_text, replication_text))
        self.wait(1.5)

        # Step 8: Summary - Key Takeaway
        summary_title = Text("The Cycle of Life", color=YELLOW).to_edge(UP, buff=1)
        summary_point1 = Text("- Single cells divide for population growth.", color=BLUE).scale(0.8).shift(UP * 1)
        summary_point2 = Text("- Multicellular organisms use Mitosis for growth and repair.", color=TEAL).scale(0.8).next_to(summary_point1, DOWN, aligned_edge=LEFT)
        summary_point3 = Text("- Meiosis creates specialized cells for reproduction.", color=PURPLE).scale(0.8).next_to(summary_point2, DOWN, aligned_edge=LEFT)

        self.play(Write(summary_title))
        self.wait(1.5)
        self.play(Write(summary_point1))
        self.wait(1.5)
        self.play(Write(summary_point2))
        self.wait(1.5)
        self.play(Write(summary_point3))
        self.wait(3)

        self.play(FadeOut(VGroup(summary_title, summary_point1, summary_point2, summary_point3, meiosis_text, new_cell1, new_cell2, new_cell1_label, new_cell2_label)))
        self.wait(2)

        final_text = Text("Cell division is fundamental to all life!", color=GOLD).scale(1.2)
        self.play(Write(final_text))
        self.wait(3)

        self.play(FadeOut(final_text))
        self.wait(2)