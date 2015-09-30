# coding=utf-8
from __future__ import absolute_import

import octoprint.plugin
import octoprint.events
import subprocess

class OctoPlugPlugin(  octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin,
					   octoprint.plugin.SimpleApiPlugin,
					   octoprint.plugin.EventHandlerPlugin):
					   
	
	def on_after_startup(self):
		self._logger.info("OctoPlugPlugin started!")
		self.currentlayer = 0
		self.printing = False

	def get_settings_defaults(self):
		return dict(
			ip="192.168.0.172",
			port="10000",
			usr="admin",
			pwd="",
			layer="3"
		)

	def get_template_configs(self):
		return [
			dict(type="settings", custom_bindings=False)
		]

	def get_assets(self):
		return dict(
			js=["js/octoplug.js"]
		)
	
	def get_api_commands(self):
		return dict(
			plugOn=[],
			plugOff=[]
		)

	def changePlugStatus(self, state):
		if state == "on" or state == "ON":
			self._logger.info("Ediplug turned on")	
			subprocess.Popen("python "+self._basefolder+"/smartplug.py -H "+self._settings.get(["ip"])+" -C "+self._settings.get(["port"])+" -l "+self._settings.get(["usr"])+" -p "+self._settings.get(["pwd"])+ " -s ON", shell=True)
		elif state == "off" or state == "OFF":
			self._logger.info("Ediplug turned off")
			subprocess.Popen("python "+self._basefolder+"/smartplug.py -H "+self._settings.get(["ip"])+" -C "+self._settings.get(["port"])+" -l "+self._settings.get(["usr"])+" -p "+self._settings.get(["pwd"])+ " -s OFF", shell=True)
	
	def on_api_command(self, command, data):
		if command == "plugOn":
			self.changePlugStatus("on")
		elif command == "plugOff":
			self.changePlugStatus("off")
				
	def onboardFanHook(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		if cmd and cmd == "M106":
			self.changePlugStatus("on")
		elif cmd and cmd == "M106 S0":
			self.changePlugStatus("off")
	
	def on_event(self, event, payload):
		if event == octoprint.events.Events.PRINT_STARTED:
			self.currentlayer = 0
			self.printing = True
			
		elif event == "ZChange":
			if self.printing == True:
				self.currentlayer += 1
				if str(self.currentlayer) == str(self._settings.get(["layer"])):
					self.changePlugStatus("on")
					
		elif event == "PrintFailed" or event == "PrintDone" or event == "PrintCancelled" or event == "PrintPaused":
			self.changePlugStatus("off")
			self.printing = False
			
		elif event == "PrintResumed":
			self.changePlugStatus("on")
			self.printing = True

		
__plugin_name__ = "OctoPlug"
__plugin_implementation__ = OctoPlugPlugin()
__plugin_hooks__ = {"octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.onboardFanHook}
