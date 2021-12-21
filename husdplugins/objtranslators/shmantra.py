import husd
from pxr import UsdLux

class ShmantraLightTranslator(husd.objtranslator.Translator):
    def primType(self):
        return 'SphereLight'
    def populatePrim(self, prim, referenced_node_prim_paths, force_active):
        super(ShmantraLightTranslator, self).populatePrim(prim, referenced_node_prim_paths, force_active)
        lgt = UsdLux.SphereLight(prim)
        self.populateAttr(lgt.CreateRadiusAttr(), self._node.parm('radius'))

def registerTranslators(manager):
    manager.registerTranslator('shmantra_light', ShmantraLightTranslator)
