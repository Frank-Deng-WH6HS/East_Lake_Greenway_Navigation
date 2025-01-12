#ELGW-GIS矢量数据重投影

#作者: Frank-Deng-WH6HS <enter_the_dragon@foxmail.com>

#引用的第三方python开源代码库项目: 
#   pyproj - MIT License
#   shapely - BSD License

#处理几何信息
import shapely; 
import shapely.geometry as shplgeo, shapely.affinity as shplaffin; 
import shapely.ops as shplops; 
#投影变换
import pyproj; 

#定义投影变换函数
#东湖绿道基础数据使用UTM Zone 49N分带投影坐标系表示, 但地图输出界面仅支持WGS84地理坐标数据的
#输入和输出(即使其内部使用了其他的投影算法用于将图形显示在GUI中)

#正向变换公式
__wgs_to_utm349__ = pyproj.Transformer.from_crs( 
    "EPSG:4326", #WGS 1984 Geodesic
    'EPSG:32649', #WGS 1984 / UTM 3° Zone 49
).transform; 

#逆向变换公式
__utm349_to_wgs__ = pyproj.Transformer.from_crs( 
    'EPSG:32649', #WGS 1984 / UTM 3° Zone 49
    "EPSG:4326", #WGS 1984 Geodesic
).transform; 

#地理坐标转UTM直角坐标
def forward_convert(geoms: shplgeo.base.BaseGeometry) -> shplgeo.base.BaseGeometry: 
    #注意: pyproj当中, WGS的坐标顺序是(lat, lon), 但地图界面显示需要(lon, lat), 
    #正向转换(WGS->UTM)前和反向转换(UTM->WGS)后, 均需要调换两个坐标的顺序
    converted = shplops.transform( \
        lambda lon, lat: __wgs_to_utm349__(lat, lon), geoms \
    ); 
    return(converted); 

#UTM投影坐标转地理坐标
def backward_convert(geoms: shplgeo.base.BaseGeometry) -> shplgeo.base.BaseGeometry: 
    converted = shplops.transform( \
        lambda x, y: __utm349_to_wgs__(x, y), geoms \
    ); 
    converted = shplaffin.affine_transform(converted, [0, 1, 1, 0, 0, 0])
    return(converted); 
