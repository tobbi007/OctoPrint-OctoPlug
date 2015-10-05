# coding=utf-8
from __future__ import absolute_import
from . import smartplug

import octoprint.plugin
import octoprint.events

class OctoPlugPlugin(  octoprint.plugin.StartupPlugin,
                       octoprint.plugin.TemplatePlugin,
                       octoprint.plugin.SettingsPlugin,
                       octoprint.plugin.AssetPlugin,
					   octoprint.plugin.SimpleApiPlugin,
					   octoprint.plugin.EventHandlerPlugin,
					   octoprint.plugin.ProgressPlugin):
					   
	
	def on_after_startup(self):
		self._logger.info("OctoPlugPlugin started!")
		self.currentlayer = 0
		self.printing = False
		self.ediplug = smartplug.SmartPlug(self._settings.get(["ip"]), self._settings.get(["port"]), (self._settings.get(["usr"]),self._settings.get(["pwd"])))

	def get_settings_defaults(self):
		return dict(
			enabled=True,
			ip=None,
			port=None,
			usr=None,
			pwd=None,
			triggerGcode=True,
			valueGcode="RepRap",
			triggerLayer=False,
			valueLayer="3",
			triggerPercentage=False,
			valuePercentage="2"
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
		
	def changePlugState(self, state):
		if self._settings.get(["enabled"]):
			self.ediplug.state = state
	
	
	def checkGcodeTrigger(self, gcode, cmd):
		if self._settings.get(["valueGcode"]) == "MakerBot":
			if gcode == "M126":
				self.changePlugState("ON")
			if gcode == "M127":
				self.changePlugState("OFF")
		
		if gcode == "M106" and "S0" not in cmd:
			self.changePlugState("ON")
		if (gcode == "M106" and "S0" in cmd) or gcode == "M107":
			self.changePlugState("OFF")
	
	def gcodeFanHook(self, comm_instance, phase, cmd, cmd_type, gcode, *args, **kwargs):
		if self._settings.get(["triggerGcode"]):
			self.checkGcodeTrigger(gcode, cmd)
	
	def on_api_command(self, command, data):
		if command == "plugOn":
			self.changePlugState("ON")
		elif command == "plugOff":
			self.changePlugState("OFF")
	
	def on_print_progress(self, location, path, progress):
		self._logger.info("Progess: "+ str(progress))
		if self._settings.get(["triggerPercentage"]):
			if str(progress) == self._settings.get(["valuePercentage"]):
				self.changePlugState("ON")
	
	def on_event(self, event, payload):
		if self._settings.get(["triggerLayer"]):
			if event == "PrintStarted":
				self.currentlayer = 0
				self.printing = True
				
			elif event == "ZChange":
				self._logger.info(payload)
				if self.printing == True:
					self.currentlayer += 1
					if str(self.currentlayer) == str(self._settings.get(["valueLayer"])):
						self.changePlugState("ON")
				
			elif event == "PrintResumed" and self.currentlayer > self._settings.get(["valueLayer"]):
				self.changePlugState("ON")
				self.printing = True
		
		if event == "PrintFailed" or event == "PrintDone" or event == "PrintCancelled" or event == "PrintPaused":
				self.changePlugState("OFF")
				self.printing = False
		
		if event == "SettingsUpdated":
			self.ediplug = smartplug.SmartPlug(self._settings.get(["ip"]), self._settings.get(["port"]), (self._settings.get(["usr"]),self._settings.get(["pwd"])))

	
__plugin_name__ = "OctoPlug"
__plugin_implementation__ = OctoPlugPlugin()
__plugin_hooks__ = {"octoprint.comm.protocol.gcode.queuing": __plugin_implementation__.gcodeFanHook}
