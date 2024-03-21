from studyo import *
from itertools import combinations
import math 
import numpy as np 

 

VERTICES = [[0,0, 0], [0, 4, 0], [3, 0, 0]]


def get_line_normal(x):
    r = x.get_end() - x.get_start()
    U_r = r / np.sqrt(np.sum(r**2)) 
    return np.array([U_r[1], -U_r[0], 0])


class Nasser(StudyoScene):
    def construct(self):
        super().__init__()
        triangle = CharCreature(Polygon(*VERTICES, fill_color=TEAL, color=TEAL, fill_opacity=1), eyes_scale=5, eyes_prop=[0,0]).scale(0.6)
        circle = CharCreature(Circle(radius=2, fill_opacity=1, color = PINK, fill_color=PINK), eyes_scale=5, eyes_prop=[0.5,0], eyes_buff=0.15).scale(0.6)
        chars = VGroup(triangle, circle).arrange(buff= 1)
        
        with self.voiceover(text= "Welcome to our video on Introduction to Trigonometry. We're going to make trigonometry easy for you, step-by-step") as tracker:
            self.title_animation(text="Trigonometry", chars=chars)

        SL = 0.5
        sq = Polygon([0,0,0],[0,SL,0], [SL,SL,0], [SL,0,0], fill_color=YELLOW, color=YELLOW, fill_opacity=0, stroke_width=6).shift(LEFT+ UP*1.5)
        
        with self.voiceover(text= "Let's start simple. See this triangle? It's not just any triangle; it's a right-angled triangle") as tracker:
            t = triangle.body.copy().shift(UP*1.5)
            self.play(t.animate.become(Polygon(*VERTICES, fill_color=TEAL, color=TEAL, fill_opacity=0).shift(LEFT + UP*1.5)), run_time=0.4*tracker.duration)
            self.play(triangle.look_at(DOWN * 0.3 + LEFT))
            self.play(triangle.blink())
            self.play(DrawBorderThenFill(sq), run_time=0.5*tracker.duration)
            
        sides = []
        texts = []
        COLORS = {
            ("Opposite"): RED,
            ("Adjacent"): GREEN,
            ("Hypotenuse"): BLUE,
            "\\theta": YELLOW
        }
        vertices = t.get_vertices()
        lines = [Line(p1,p2) for (p1, p2) in combinations(vertices, 2)]
        with self.voiceover(text= "when addressing an angle in a triangle we have three relative sides to it") as tracker:
            self.play(FadeOut(sq), run_time=tracker.duration*0.2)
            adressed_angle = Angle(lines[2], lines[1], radius=1.5, stroke_width=3, color=YELLOW, quadrant=(-1,-1))
            angle_text = MathTex("\\theta", color=YELLOW).move_to(adressed_angle.get_center()).scale(0.8).shift(RIGHT*0.1)
            self.play(Create(adressed_angle), Write(angle_text), run_time=tracker.duration*0.8)
            
        for ((start, end), color, name, direction) in zip(combinations(VERTICES, 2), [*COLORS.values()], [*COLORS.keys()], [LEFT,DOWN, RIGHT]):
            line = Line(start, end , color=color, stroke_width= 9).shift(LEFT + UP*1.5)
            text = Tex(name, color=color).move_to(line.get_center() + direction * 0.3 ).scale(0.8).rotate(line.get_angle())
            with self.voiceover(text= f"the {name}") as tracker:
                self.play( FadeIn(text), FadeIn(line), run_time=tracker.duration)
            texts.append(text)
            sides.append(line)
        self.play( FadeOut(t))
        
        opp, adj, hyp = texts
        _opp, _adj, _hyp = sides
        
        TRIG_FUNCS = [
            {
                "frac": [opp, hyp],
                "example": [4, 5],
                "tex": r"\sin",
                "name": "sine"
                
            },
            {
                "frac": [adj, hyp],
                "example": [3, 5],
                "tex": r"\cos",
                "name": "cosine"
            },
            {
                "frac": [opp, adj],
                "example": [4, 3],
                "tex": r"\tan",
                "name": "tangent"
            }
        ]
        COLOR_MAP = {
            "\\sin": RED,
            "\\cos": BLUE,
            "\\theta": YELLOW
            
        }
        prev_eq = None
        for i,f in enumerate(TRIG_FUNCS):
            nom, den = map(lambda x:x.get_tex_string(),f["frac"]) 
            name = f["name"] 
            eq = MathTex(f["tex"],"(","\\theta", ")", r" = {{", nom,'}',r" \over",'{', den,"}}").set_color_by_tex_to_color_map(COLORS).shift( 1.3*DOWN + LEFT * 1.7).scale(1.1)
            if prev_eq:
                eq = eq.next_to(prev_eq,  DOWN *1.5).align_to(prev_eq, LEFT)
            prev_eq = eq
            num1, num2 = map(str,f["example"])
            result = str(round(int(num1)/int(num2),2))
            with self.voiceover(text= f"{name} of this angle is the length of the {nom} side divided by the {den}") as tracker:
                self.play(TransformMatchingTex(Group(*f["frac"]).copy(), eq), run_time=0.5*tracker.duration)
                self.wait(0.5*tracker.duration)
            self.wait(0.3)
            eq2 =  MathTex(r" = {", num1,r"\over",num2,r"}  = ", result, ).set_color(WHITE).next_to(eq, RIGHT).set_color_by_tex_to_color_map(dict(zip(["4", "3", "5"],COLORS.values()))).scale(1.1).set_color_by_tex("1.33", WHITE)
            with self.voiceover(text= f"If the {nom} side is {num1} units and the {den} is {num2} units, the {name} is {result}.") as tracker:
                self.play(Write(eq2), run_time=0.5*tracker.duration)
                self.wait(0.5*tracker.duration)
        
        self.wait(1)

        c = Circle(radius=2, fill_opacity=0, color = PINK, fill_color=PINK)
        R = c.get_radius()
        theta = math.pi/6
        angle_tracker = ValueTracker(30)
        get_th = lambda : np.radians(angle_tracker.get_value())
        get_projection = lambda : np.array([R*math.cos(get_th()), R*math.sin(get_th()), 0])
        get_pt = lambda : c.get_center() + get_projection()
        self.clear()
        first = "Fdrkg dfj glk"
        with self.voiceover(text= f"Now lets {first} talk about the unit circle. It's a way to understand angles and trigonometry.") as tracker:
            self.play(circle.body.copy().animate.become(c).move_to(ORIGIN))
            self.play(circle.look_at(DOWN + LEFT))
            self.play(circle.blink())
            
        line1 = Line(c.get_center(), c.get_center() + RIGHT*R)
        projection = np.array([R*math.cos(theta), R*math.sin(theta), 0])
        circle_pt = Point(c.get_center() + projection)
        line2 = Line(c.get_center(), circle_pt)
        brace = Brace(line1)
        length = Integer(number=1).set_color(ORANGE).next_to(brace, DOWN * 1.5)
        adressed_angle = Angle(line1, line2, radius=1, stroke_width=3, color=YELLOW, quadrant=(1, 1))
        angle_text = MathTex("\\theta", color=YELLOW).move_to(adressed_angle.get_center()).scale(0.8).shift(LEFT*0.1)
        with self.voiceover(text= f"When we draw a line from the centre of the circle to the boundary, that line has a length of 1 because it's a unit circle.") as tracker:
            self.play(Create(line1), run_time=0.3*tracker.duration)
            self.play(FadeIn(brace), run_time=0.3*tracker.duration)
            self.play(Write(length), run_time=0.3*tracker.duration)
        
        with self.voiceover(text= f"The angle this line makes with the horizontal line is what we'll focus on.") as tracker:
            self.play(Create(line2), Create(adressed_angle), Write(angle_text), run_time=0.2*tracker.duration)
            self.play(line2.animate().set_color(YELLOW), line1.animate().set_color(YELLOW), run_time=0.3*tracker.duration)
            self.play(FadeOut(brace), FadeOut(length))
            
        with self.voiceover(text= f"that vertical line has a length of sin of the angle, while the horizontal line has a length of cos of the angle.") as tracker:
            y = always_redraw(lambda : Line(circle_pt, c.get_center() + np.array([R*math.cos(theta),0,0])).set_color(RED))
            y_text = always_redraw(lambda :MathTex(r"\sin", "(", r"\theta",")").next_to(y, get_line_normal(y)).set_color_by_tex_to_color_map(COLOR_MAP).scale(0.5))
            x = always_redraw(lambda :Line(c.get_center(), c.get_center() + np.array([R*math.cos(theta),0,0])).set_color(BLUE))
            x_text = always_redraw(lambda :MathTex(r"\cos", "(", r"\theta",")").next_to(x, get_line_normal(x)).set_color_by_tex_to_color_map(COLOR_MAP).scale(0.5))
            adressed_angle.add_updater(lambda m: m.become(Angle(line1, line2, radius=1, stroke_width=3, color = YELLOW)))
            self.play(Write(y_text), FadeIn(y), run_time=0.5*tracker.duration)
            self.play(Write(x_text), FadeIn(x), run_time=0.5*tracker.duration)
        with self.voiceover(text= f"So, we've just scratched the surface of trigonometry. But what if I told you there's a magic circle that can make understanding angles and trigonometric functions even easier? Stay tuned for our next video where we dive into the mesmerising world of the Unit Circle.") as tracker:
            self.play(FadeOut(VGroup(y_text, x_text, angle_text)))
            self.play(angle_tracker.animate.set_value(360), run_time=tracker.duration * 0.6)
            self.clear() 
            self.play(chars.animate.scale(2).move_to(ORIGIN))
            self.wait(0.5*tracker.duration)