#ELGW-GIS可交互地图界面: 基于计算几何库shapely和第三方Tkinter地图插件Mapview

#作者: Frank-Deng-WH6HS <enter_the_dragon@foxmail.com>

#引用的第三方python开源代码库项目: 
#   tkintermapview - CC0
#   shapely - BSD License

#操作目录和文件
import sys, os; __script_dir = os.path.dirname(__file__); 
#处理几何信息
import shapely; 
import shapely.geometry as shplgeo, shapely.affinity as shplaffin; 
import shapely.ops as shplops; 
#数值计算和函数处理
from functools import partial; 
#用户界面
import tkinter as tk; 
import tkintermapview as tkmvw; 

#导入工程目录下的自定义类
__repo_root = os.path.abspath(os.sep.join([__script_dir, os.pardir])); 
sys.path.append(__repo_root); 
#通过pyshp从shp文件导入并构建的AttributiveGeometry类
from File_IO import ELGW_Load; 

#RGB颜色对象, 可设置色彩值, 并表示为HTML形式的24位色彩字符串
#临时定义, 后续版本可能会改用第三方库. 
class RGBColor(): 
    
    def __init__(self, rgb=(0, 0, 0)): 
        #处理非法输入
        if len(rgb) == 3: #数据结构正确
            if any(band >= 2 ** 8 for band in rgb): #数据取值错误
                raise ValueError(
                    f'Elements in rgb cannot be numbers greater than 255. '
                ); 
            elif any(band < 0 for band in rgb): #数据取值错误
                raise ValueError(
                    f'Elements in rgb cannot be numbers less than 0. '
                ); 
            else: 
                self.__rgb = rgb; 
        else: #数据结构错误
            raise TypeError(f'Invalid type for rgb'); 
    
    def __repr__(self): 
        return(f'{RGBColor.__name__}({self.__rgb})')
        
    #获取或修改颜色值(由红, 绿, 蓝三色强度组成的三元组)
    @property
    def rgb(self): 
        return self.__rgb; 
    @rgb.setter
    def rgb(self, band_arr): 
        self.__init__(rgb = band_arr); 
        
    #获取颜色的HTML文本
    @property
    def html_color(self): 
        return "#" + bytes(self.__rgb).hex(); 

#为绘制的shapely图形指定执行重绘任务的地图缩放级别范围, 以及符号系统, 形成一个对象
class RedrawableGeometry(): 
    
    LOWERMOST_ZOOM = 1; 
    UPPERMOST_ZOOM = 19; 
    BORDER_COLOR_DEFAULT = RGBColor((0, 109, 184)); 
    BORDER_WIDTH_DEFAULT = 5; 
    
    #初始化
    def __init__(self, shape: ELGW_Load.AttributiveGeometry, 
        min_zoom=None, max_zoom=None, border_color=None, border_width=None
    ): 
        if type(shape) is ELGW_Load.AttributiveGeometry: 
            #d导入几何和属性信息
            self.shapeTypeName = shape.shapeTypeName; 
            self.geometry = shape.geometry; 
            self.attribute = shape.attribute; #预留, 后期拟定用于在点击图形后提示部分属性
            #处理非法的缩放级别, 确保 1 ≤ 最小缩放级别 ≤ 最大缩放级别 ≤ 19
            if min_zoom == None: 
                 min_zoom = RedrawableGeometry.LOWERMOST_ZOOM; 
            if max_zoom == None: 
                max_zoom = RedrawableGeometry.UPPERMOST_ZOOM
            if border_color == None: 
                border_color = RedrawableGeometry.BORDER_COLOR_DEFAULT; 
            if border_width == None: 
                border_width = RedrawableGeometry.BORDER_WIDTH_DEFAULT; 
            self.__min_zoom = max(
                RedrawableGeometry.LOWERMOST_ZOOM, 
                int(min_zoom)
            ); 
            self.__max_zoom = min(
                RedrawableGeometry.UPPERMOST_ZOOM, 
                int(max_zoom)
            ); 
            self.__max_zoom = max(self.__max_zoom, self.__min_zoom); 
            self.__border_color = border_color; 
            #处理非法的线宽, 确保 1 ≤ 线宽  
            self.__border_width = max(border_width, 1); 
        else: 
            return TypeError; 
        
    #定义图形在地图查看器上显示时的最小, 最大缩放级别属性
    #最小缩放级别
    @property
    def min_zoom(self): 
        return self.__min_zoom; 
    @min_zoom.setter
    def min_zoom(self, zoom_lvl): 
        self.__min_zoom = min(
            max(RedrawableGeometry.LOWERMOST_ZOOM, 
            int(zoom_lvl)), self.__max_zoom
        ); 
        
    #最大缩放级别
    @property
    def max_zoom(self): 
        return self.__max_zoom; 
    @max_zoom.setter
    def max_zoom(self, zoom_lvl): 
        self.__max_zoom = max(
            min(RedrawableGeometry.UPPERMOST_ZOOM, 
            int(zoom_lvl)), self.__min_zoom
        ); 
        
    #符号系统
    #边界颜色(点, 线的颜色)
    @property
    def border_color(self): 
        return self.__border_color; 
    @border_color.setter
    def border_color(self, color): 
        self.__border_color = color; 
        
    #边界宽度(点的大小或线的粗细)
    @property
    def border_width(self): 
        return self.__border_width; 
    @border_width.setter
    def border_width(self, wdt): 
        self.__border_width = max(wdt, 1); 

#定义改良的mapview查看器, 使之支持重绘功能
#重绘的目的是让查看器只绘制窗口范围内可见的矢量图形, 减少用户在平移地图时的延迟卡顿
class TkMapViewRedrawable(tkmvw.map_widget.TkinterMapView): 
    
    def __init__(self, window, width: int = 800, height: int = 600): 
        super().__init__(window, width=width, height=height); 
        #禁用联网加载底图瓦片服务(将网址设置为"空白页")
        #警告! OpenStreetMap中的部分制图要素, 不符合中国现行法律法规
        self.set_tile_server("about:blank"); 
        self.layers = []; 
        
    #定义查看器"窗口中心点经纬度"属性
    @property
    def position(self): 
        return self.get_position(); 
    @position.setter
    def position(self, pos_new): 
        self.set_position(pos_new); 
        
    #绘图区域边界的经纬度("四至点经纬度", 不能直接更改)
    #返回结果为四元组: (最西端经度, 最南端纬度, 最东端经度, 最北端纬度)    
    def boundary_latlon(self): 
        ymin, xmin = self.convert_canvas_coords_to_decimal_coords(
            0, self.height); 
        ymax, xmax = self.convert_canvas_coords_to_decimal_coords(
            self.width, 0); 
        return(xmin, ymin, xmax, ymax); 
        
    #重绘功能
    def redraw_annotation(self, event): 
        #擦除原来绘制的内容
        self.delete_all_path(); 
        #计算地图界面当前的显示范围
        xmin, ymin, xmax, ymax = self.boundary_latlon(); 
        for layer in self.layers: 
            #使用地图当前的显示范围对路段进行裁剪
            geoms_clipped = shplops.clip_by_rect(
                layer.geometry, xmin, ymin, xmax, ymax
            ); 
            #将裁剪后的每一部分绘制在地图界面上
            if type(geoms_clipped) is shplgeo.multilinestring.MultiLineString: 
                for part in geoms_clipped: 
                    x_list, y_list = part.coords.xy; 
                    self.set_path(
                        list(zip(tuple(y_list), tuple(x_list))), 
                        color=layer.border_color.html_color, 
                        width=layer.border_width
                    ); 
            elif type(geoms_clipped) is shplgeo.multipoint.MultiPoint: 
                for part in geoms_clipped: 
                    x_list, y_list = part.xy; 
                    self.set_path(((y_list, x_list)) * 2, 
                        color=layer.border_color.html_color, 
                        width=layer.border_width
                    ); 