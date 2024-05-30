"""
This is a Python script that contains the ConsortDiagram class. This class is used to create Consort Diagrams using the schemdraw library. The class has methods to add data, stage, and other information to the diagram. The class also has methods to add arrows and lines between the boxes in the diagram. The diagram can be displayed using the display_svg method.
Parameters:
    - data: pandas DataFrame
    - fontsize: float
    - unit: float
    - box_dimension: tuple
    - stage_box_dimension: tuple
    - stage_box_th: float
Attributes:
    - diagram: schemdraw.Drawing
    - data: pandas DataFrame
    - box_dimension: tuple
    - stage_box_dimension: tuple
    - stage_box_th: float
    - unit: float
    - boxes_obj: dict
    - stage_boxes_obj: dict
    - boxes_data: dict
    - stage_boxes_data: dict
    - other_data: dict
Methods:
    - add_arrow: Add an arrow between two boxes in the diagram.
    - add_line: Add a line between two points in the diagram.
    - get_coordinates: Get the coordinates of a box in the diagram.
    - display_svg: Display the diagram as an SVG image.
    - _create_box: Create a box for the diagram.
    - update_label: Update the label of a box in the diagram.
    - add_consort_data: Add data to the diagram.
    - _create_stage_box: Create a stage box for the diagram.
    - add_stage_data: Add stage data to the diagram.
    - add_other_data: Add other data to the diagram.
    - _generate_other_box: Generate a box for other data in the diagram.
    - add_other_box: Add a box for other data to the diagram.
    - get_drawing: Get the schemdraw.Drawing object of the diagram.
"""
import streamlit as st
import numpy as np
import pandas as pd
import schemdraw
from schemdraw import flow, ImageFormat
from typing import Union, Literal

class ConsortDiagram():
    def __init__(self, data:pd.DataFrame, fontsize:float, unit:float=1, box_dimension: tuple = (14, 1), stage_box_dimension: tuple = (3, 1), stage_box_th: float=90.0):
        self.diagram = schemdraw.Drawing(fontsize=fontsize, unit=unit)
        self.data = data
        
        self.box_dimension = box_dimension
        self.stage_box_dimension = stage_box_dimension
        self.stage_box_th = stage_box_th
        self.unit = unit
        
        self.boxes_obj = {} # label: flow obj
        self.stage_boxes_obj = {} # label: flow obj for stage box
        self.boxes_data = {} # label: count, x, y
        self.stage_boxes_data = {} # label: x, y
        self.other_data = {}
    
    def add_arrow(self, start: Union[tuple[str,Literal['E','S','W','N']],tuple[float,float]], end: Union[tuple[str,Literal['E','S','W','N']],tuple[float,float]]):
        '''
        Add an arrow between two boxes in the diagram.
        Parameters:
            - start: tuple[str,Literal['E','S','W','N']] or tuple[float,float]
                - If the start is a tuple of strings and a direction, the arrow will start from the box with the label and direction.
                - If the start is a tuple of floats, the arrow will start from the coordinates.
            - end: tuple[str,Literal['E','S','W','N']] or tuple[float,float]
                - If the end is a tuple of strings and a direction, the arrow will end at the box with the label and direction.
                - If the end is a tuple of floats, the arrow will end at the coordinates.
        Returns:
            - None
        Examples:
            - add_arrow(('Box 1', 'E'), ('Box 2', 'W'))
            - add_arrow(('Box 1', 'E'), (10, 5))
            - add_arrow((10, 5), ('Box 2', 'W'))
            - add_arrow((10, 5), (20, 5))
        '''
        start_obj = None
        end_obj = None

        start1, start2 = start
        end1, end2 = end
        if isinstance(start1, str) and isinstance(start2, str) and isinstance(end1, str) and isinstance(end2, str):
            start_var_name = start1.lower().replace(' ', '_')
            end_var_name = end1.lower().replace(' ', '_')
            start_obj = self.boxes_obj[start_var_name]
            end_obj = self.boxes_obj[end_var_name]

            arrow = flow.Arrow().at(getattr(start_obj, start2)).to(getattr(end_obj, end2))
            self.diagram.add(arrow)
            
        elif isinstance(start1, str) and isinstance(start2, str) and isinstance(end1, float) and isinstance(end2, float):
            start_var_name = start1.lower().replace(' ', '_')
            start_obj = self.boxes_obj[start_var_name]

            if start2 == 'E':
                length = abs(end1 - start_obj.E.x)
                arrow = flow.Arrow().at(start_obj.E).right().length(length/self.unit)
            elif start2 == 'S':
                length = abs(end2 - start_obj.S.y)
                arrow = flow.Arrow().at(start_obj.S).down().length(length/self.unit)
            elif start2 == 'W':
                length = abs(end1 - start_obj.W.x)
                arrow = flow.Arrow().at(start_obj.W).left().length(length/self.unit)
            else:
                length = abs(end2 - start_obj.N.y)
                arrow = flow.Arrow().at(start_obj.N).up().length(length/self.unit)

            self.diagram.add(arrow)

        elif isinstance(start1, float) and isinstance(start2, float) and isinstance(end1, str) and isinstance(end2, str):
            end_var_name = end1.lower().replace(' ', '_')
            end_obj = self.boxes_obj[end_var_name]

            if end2 == 'E':
                length = abs(start1 - end_obj.E.x)
                arrow = flow.Arrow().at((start1, start2)).left().length(length/self.unit)
            elif end2 == 'S':
                length = abs(start2 - end_obj.S.y)
                arrow = flow.Arrow().at((start1, start2)).up().length(length/self.unit)
            elif end2 == 'W':
                length = abs(start1 - end_obj.W.x)
                arrow = flow.Arrow().at((start1, start2)).right().length(length/self.unit)
            else:
                length = abs(start2 - end_obj.N.y)
                arrow = flow.Arrow().at((start1, start2)).down().length(length/self.unit)
            
            self.diagram.add(arrow)

        elif isinstance(start1, float) and isinstance(start2, float) and isinstance(end1, float) and isinstance(end2, float):
            if start1 == end1:
                arrow = flow.Arrow().at((start1, start2)).toy((end1, end2))
            elif start2 == end2:
                arrow = flow.Arrow().at((start1, start2)).tox((end1, end2))
            else:
                raise ValueError("Invalid start and end coordinates")

            self.diagram.add(arrow)

        return

    def add_line(self, start_x: float, start_y: float, end_x: float, end_y: float):
        '''
        Add a line between two points in the diagram.
        Parameters:
            - start_x: float
            - start_y: float
            - end_x: float
            - end_y: float
        Returns:
            - None
        Note: 
            - The line can be horizontal or vertical.
        Raises:
            - ValueError: If the start and end coordinates are not valid.
        Examples:
            - add_line(10, 5, 20, 5)
        '''
        if start_x == end_x:
            line = flow.Line().at((start_x, start_y)).toy((end_x, end_y))
        elif start_y == end_y:
            line = flow.Line().at((start_x, start_y)).tox((end_x, end_y))
        else:
            raise ValueError("Invalid start and end coordinates")

        self.diagram.add(line)
        
        return

    def get_coordinates(self, label: str, anchor: str):
        '''
        Get the coordinates of a box in the diagram.
        Parameters:
            - label: str
            - anchor: str
                - E: East
                - S: South
                - W: West
                - N: North
        Returns:
            - tuple[float, float]
        Examples:
            - get_coordinates('Box 1', 'E')
        '''
        var_name = label.lower().replace(' ', '_')
        flow_obj = self.boxes_obj[var_name]

        return getattr(getattr(flow_obj, anchor), 'x'), getattr(getattr(flow_obj, anchor), 'y')

    def display_svg(self, max_width: int=10):
        '''
        Show the diagram as an SVG image.
        Parameters:
            - max_width: int
                - The maximum width of the diagram in percentage.
        Returns:
            - None
        Examples:
            - display_svg(100)
        '''
        img = self.diagram.get_imagedata(ImageFormat.SVG)
        html = f'<div style="max-width: {max_width}%; height: auto;">{img.decode("utf-8")}</div>'
        st.write(html, unsafe_allow_html=True)

        return
   
    def _create_box(self, label: str, count: int, x: float, y: float, w: float=np.nan, h: float=np.nan, details: list[str]=['']):
        '''
        Create a box for the diagram.
        Parameters:
            - label: str
            - count: int
            - x: float
            - y: float
            - w: float
            - h: float
            - details: list[str]
        Returns:
            - flow.Box
        Examples:
            - _create_box('Box 1', 10, 5, 2)
        '''
        if np.isnan(w):
            w=self.box_dimension[0]
        if np.isnan(h):
            h=self.box_dimension[1]
            
        label_text = f'{label.split("--")[0]} (n = {count})'
        return flow.Box(w=w, h=h).label(label_text, loc='center', halign='center', valign='center').at((x, y))
    
    def update_label(self, key: str, count: int):
        '''
        Update the label of a box in the diagram.
        Parameters:
            - key: str
            - count: int
        Returns:
            - None
        Examples:
            - update_label('Box 1', 10)
        '''
        var_name = key.lower().replace(' ', '_')
        flow_obj = self.boxes_obj[var_name]

        label_text = f'{key.split("--")[0]} (n = {count})'
        st.write(f"original label {flow_obj.label} new label {label_text}")
        flow_obj.label(label_text)
        
        return
    
    def add_consort_data(self, key: str, count: int, x: float, y: float, w: float=np.nan, h: float=np.nan):
        '''
        Add data to the diagram.
        Parameters:
            - key: str
            - count: int
            - x: float
            - y: float
            - w: float
            - h: float
        Returns:
            - None
        Raises:
            - ValueError: If the key already exists in consort_data.
        Examples:
            - add_consort_data('Box 1', 10, 5, 2)
        '''
        if np.isnan(w):
            w=self.box_dimension[0]
        if np.isnan(h):
            h=self.box_dimension[1]
            
        if key not in self.boxes_data:
            self.boxes_data[key] = [count, x, y]
            
            box = self._create_box(key, count, x, y, w, h)
            self.diagram.add(box)
            var_name = key.lower().replace(' ', '_')
            self.boxes_obj[var_name] = box
            
            return
        else:
            raise ValueError(f"{key} already exists in consort_data.")
        
    def _create_stage_box(self, label, x, y, w, h, fill_color, font_color, cornerradius: float, th: float):
        '''
        Private method for creating a stage box for the diagram.
        Parameters:
            - label: str
            - x: float
            - y: float
            - w: float
            - h: float
            - fill_color: str
            - font_color: str
            - cornerradius: float
            - th: float
        Returns:
            - flow.RoundBox
        Examples:
            - _create_stage_box('Stage 1', 5, 2)
        '''
        flow.RoundBox.defaults['fill'] = fill_color
        return flow.RoundBox(cornerradius=cornerradius, w=w, h=h).label(label, rotate=th, color=font_color).theta(th).at((x, y))
    
    def add_stage_data(self, key, x, y, w: float=np.nan, h: float=np.nan, fill_color: str='#9bc0fc', font_color: str='#0762f7', cornerradius: float=0.5, th: float=np.nan):
        '''
        Add stage data to the diagram.
        Parameters:
            - key: str
            - x: float
            - y: float
            - w: float
            - h: float
            - fill_color: str
            - font_color: str
            - cornerradius: float
            - th: float
        Returns:
            - None
        Raises:
            - ValueError: If the key already exists in stage_boxes_data.
        Examples:
            - add_stage_data('Stage 1', 5, 2)
        '''
        if np.isnan(w):
            w = self.stage_box_dimension[0]
        if np.isnan(h):
            h = self.stage_box_dimension[1]
        if np.isnan(th):
            th = self.stage_box_th
            
        if key not in self.stage_boxes_data:
            self.stage_boxes_data[key] = [x, y]
            
            box = self._create_stage_box(key, x, y, w, h, fill_color, font_color, cornerradius, th)
            self.diagram.add(box)
            var_name = key.lower().replace(' ', '_')
            self.stage_boxes_obj[var_name] = box
        else:
            raise ValueError(f"{key} already exists in consort_data.")
   
    def add_other_data(self, data_type: str, key: str, df: pd.DataFrame):
        '''
        Add other data to the diagram.
        Parameters:
            - data_type: str
            - key: str
            - df: pd.DataFrame
        Returns:
            - None
        Raises:
            - ValueError: If the key already exists.
        Examples:
            - add_other_data('Reasons for Exclusion', 'Ineligible', df)
        '''
        if '--' in key:
            data_label, data_set = key.split('--')
        else:
            data_label = key
            data_set = '1'
        
        if data_type not in self.other_data:    
            self.other_data[data_type] = {
                data_set: {
                    data_label: len(df)
                }
            }
            
        else:
            if data_set not in self.other_data[data_type]:
                self.other_data[data_type][data_set] = {
                    data_label: len(df)
                }
            else:
                if data_label not in self.other_data[data_type][data_set]:
                    self.other_data[data_type][data_set][data_label] = len(df)
                else:
                    raise ValueError(f"{key} already exists.")
                
        return
                
    def _generate_other_box(self, data_types: list[str], target_set: str, x: float, y: float, w: float, h: float, offset: tuple[float, float], ratio: float):
        '''
        Private method for generating a box for other data in the diagram.
        Parameters:
            - data_types: list[str]
            - target_set: str
            - x: float
            - y: float
            - w: float
            - h: float
            - offset: tuple[float, float]
            - ratio: float
        Returns:
            - flow.Box
        Examples:
            - _generate_other_box(['Reasons for Exclusion'], 'Ineligible', 5, 2)
        '''
        max_label_length = 0
        label = ''
        total_count = None
        
        for data_type in data_types:
            for key, value in self.other_data.get(data_type, {}).items():
                if key == target_set:
                    total_count = sum(value.values())
                    max_label_length = max(max_label_length, len(f'{data_type} (n = {total_count})\n'))
                    label += f'{data_type} (n = {total_count})\n'
                    
                    for reason, count in value.items():
                        current_line = f'• {reason} (n = {count})\n'
                        label += current_line
                        max_label_length = max(max_label_length, len(current_line))
        
        parent_length = max(len(f'{data_type} (n = {total_count})\n') for data_type in data_types)
        adj_w = max(w, max_label_length // parent_length // ratio * w)
        adj_h = max(h, (len(label.split('\n')) - 1) // ratio * h)

        return flow.Box(w=adj_w, h=adj_h).label(label, loc='left', halign='left', valign='center', ofst=offset).at((x, y))
    
    def add_other_box(self, data_types, target_set, x, y, w: float=np.nan, h: float=np.nan, offset: tuple=(0.4, -0.2), ratio: float=1.5):
        '''
        Add a box for other data to the diagram.
        Parameters:
            - data_types: list[str]
            - target_set: str
            - x: float
            - y: float
            - w: float
            - h: float
            - offset: tuple[float, float]
            - ratio: float
        Returns:
            - None
        Examples:
            - add_other_box(['Reasons for Exclusion'], 'Ineligible', 5, 2)
        '''
        if np.isnan(w):
            w=self.box_dimension[0]
        if np.isnan(h):
            h=self.box_dimension[1]
              
        box = self._generate_other_box(data_types, target_set, x, y, w, h, offset, ratio)
        self.diagram.add(box)
        var_name = '_'.join(str(d).lower().replace(' ', '_') for d in data_types) + f"_{str(target_set)}"
        self.boxes_obj[var_name] = box
        
        return

    def get_drawing(self):
        '''
        Get the schemdraw.Drawing object of the diagram.
        Returns:
            - schemdraw.Drawing
        '''
        return self.diagram