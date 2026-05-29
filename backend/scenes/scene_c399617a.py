from manim import *

config.background_color = BLACK

class Scene(Scene):
    def construct(self):
        title = Text("Biology", font_size=72)
        self.play(Write(title))
        self.wait(1)
        self.play(FadeOut(title))

        bio_concept = Text("Scientific Concepts & Facts", font_size=48)
        self.play(Write(bio_concept))
        self.wait(1)
        self.play(FadeOut(bio_concept))

        arrow1 = Arrow(LEFT, RIGHT, buff=1)
        circle = Circle(radius=1, color=BLUE)
        text1 = Text("Multiple Choice", font_size=24)
        text1.next_to(circle, DOWN)
        group1 = VGroup(circle, text1)

        arrow2 = Arrow(LEFT, RIGHT, buff=1)
        square = Square(side_length=1.5, color=RED)
        text2 = Text("Short Answer", font_size=24)
        text2.next_to(square, DOWN)
        group2 = VGroup(square, text2)

        VGroup(arrow1, group1).arrange(RIGHT, buff=2)
        VGroup(arrow2, group2).arrange(RIGHT, buff=2)


        self.play(Create(arrow1), Write(group1))
        self.wait(1)
        self.play(Create(arrow2), Write(group2))
        self.wait(1)

        self.play(FadeOut(VGroup(arrow1, group1, arrow2, group2)))

        question_types = Text("Various Question Types", font_size=48)
        self.play(Write(question_types))
        self.wait(2)
        self.play(FadeOut(question_types))

        self.wait(2)