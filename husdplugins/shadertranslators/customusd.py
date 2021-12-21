import re
from husd.shadertranslator import ShaderTranslator as TranslatorBase
from husd.shadertranslator import ShaderTranslatorHelper as HelperBase
from pxr import Sdf, UsdShade

class CustomShaderTranslatorHelper( HelperBase ):
    def __init__(self, translator_id, 
                 usd_stage, usd_material_path, usd_time_code):
        HelperBase. __init__( self, translator_id, 
                usd_stage, usd_material_path, usd_time_code )

    def usdRenderContextName(self, shader_node, shader_node_output_name):
        """ Returns the name of the render context used in the USD material 
            output name. In this case, a univarsal USD render context name. 
        """
        return UsdShade.Tokens.universalRenderContext

    def createUsdShader(self, shader_node, shader_node_output_name,
            usd_parent_schema):
        """ Creates and configures a single USD shader primitive 
            based on the given Houdini shader node.
            Returns a USD shader schema for the created USD primitive.
        """
        # create the USD shader
        usd_shader_path = self.usdShaderPrimitivePath(shader_node, 
                usd_parent_schema)

        # create st reader
        stReader = UsdShade.Shader.Define(self.usdStage(), usd_shader_path.AppendPath('streader'))
        stReader.CreateIdAttr('UsdPrimvarReader_float2')
        stReader.CreateInput('varname', Sdf.ValueTypeNames.Token).Set("st")

        # create texture
        filename = shader_node.parm('basecolor').eval()
        diffuseTextureSampler = UsdShade.Shader.Define(self.usdStage(), usd_shader_path.AppendPath('texture'))
        diffuseTextureSampler.CreateIdAttr('UsdUVTexture')
        diffuseTextureSampler.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(filename)
        diffuseTextureSampler.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(stReader.ConnectableAPI(), 'result')
        diffuseTextureSampler.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)

        # create preview shader
        usd_shader = self.defineUsdShader( shader_node, usd_shader_path )
        usd_shader.SetShaderId( 'UsdPreviewSurface' )
        # connect diffuse textire
        usd_shader.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).ConnectToSource(diffuseTextureSampler.ConnectableAPI(), 'rgb')

        return usd_shader



################################################################################
class CustomShaderTranslator( TranslatorBase ):
    def __init__(self):
        TranslatorBase.__init__( self )
        self.myPattern = re.compile( r'\bCUSTOMUSD\b' )

    def matchesRenderMask(self, render_mask):
        return bool( self.myPattern.search( render_mask ))

    def renderContextName(self, shader_node, shader_node_output_name):
        # Standard and USD preview shaders don't have render context name,
        # since they are applicable to all renderers.
        return UsdShade.Tokens.universalRenderContext

    def shaderTranslatorHelper(self, translator_id,
                usd_stage, usd_material_path, usd_time_code):
        return CustomShaderTranslatorHelper(translator_id,
                usd_stage, usd_material_path, usd_time_code)


standard_translator = CustomShaderTranslator()
def usdShaderTranslator():
    return standard_translator

