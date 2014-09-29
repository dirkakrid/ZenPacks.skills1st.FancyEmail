# Nothing is required in this __init__.py, but it is an excellent place to do
# many things in a ZenPack.
#
# import Globals
#
# from Products.ZenModel.ZenPack import ZenPack as ZenPackBase
# from Products.ZenUtils.Utils import unused
#
# unused(Globals)
#
#
# class ZenPack(ZenPackBase):
#
#     def install(self, dmd):
#         ZenPackBase.install(self, dmd)
#
#         # Put your customer installation logic here.
#         pass
#
#     def remove(self, dmd, leaveObjects=False):
#         if not leaveObjects:
#             # When a ZenPack is removed the remove method will be called with
#             # leaveObjects set to False. This means that you likely want to
#             # make sure that leaveObjects is set to false before executing
#             # your custom removal code.
#             pass
#
#         ZenPackBase.remove(self, dmd, leaveObjects=leaveObjects)
