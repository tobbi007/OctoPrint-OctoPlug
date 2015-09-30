##
# The MIT License (MIT)
#
# Copyright (c) 2014 Stefan Wendler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
##

__author__ = 'Stefan Wendler, sw@kaltpost.de'

import requests as req
import optparse as par
import logging as log

from xml.dom.minidom import getDOMImplementation
from xml.dom.minidom import parseString


class SmartPlug(object):

    """
    Simple class to access a "EDIMAX Smart Plug Switch SP-1101W"

    Usage example when used as library:

    p = SmartPlug("172.16.100.75", ('admin', '1234'))

    # change state of plug
    p.state = "OFF"
    p.state = "ON"

    # query and print current state of plug
    print(p.state)

    # read and print complete week schedule from plug
    print(p.schedule.__str__())

    # write schedule for on day to plug (Saturday, 11:15 - 11:45)
    p.schedule = {'state': u'ON', 'sched': [[[11, 15], [11, 45]]], 'day': 6}

    # write schedule for the whole week
    p.schedule = [
        {'state': u'ON', 'sched': [[[0, 3], [0, 4]]], 'day': 0},
        {'state': u'ON', 'sched': [[[0, 10], [0, 20]], [[10, 16], [11, 55]], [[15, 19], [15, 32]], [[21, 0], [23, 8]], [[23, 17], [23, 59]]], 'day': 1},
        {'state': u'OFF', 'sched': [[[19, 59], [21, 1]]], 'day': 2},
        {'state': u'OFF', 'sched': [[[20, 59], [21, 12]]], 'day': 3},
        {'state': u'OFF', 'sched': [], 'day': 4},
        {'state': u'OFF', 'sched': [[[0, 0], [0, 30]], [[11, 14], [14, 31]]], 'day': 5},
        {'state': u'ON', 'sched': [[[1, 42], [2, 41]]], 'day': 6}]


    Usage example when used as command line utility:

    turn plug on:

    python smartplug.py -H 172.16.100.75 -l admin -p 1234 -s ON

    turn plug off:

    python smartplug.py -H 172.16.100.75 -l admin -p 1234 -s OFF

    get plug state:

    python smartplug.py -H 172.16.100.75 -l admin -p 1234 -g

    get schedule of the whole week:

    python smartplug.py -H 172.16.100.75 -l admin -p 1234 -G

    get schedule of the whole week as python array:

    python smartplug.py -H 172.16.100.75 -l admin -p 1234 -P

    set schedule for one day:

    python smartplug.py -H 172.16.100.75 -l admin -p 1234 -S "{'state': u'ON', 'sched': [[[11, 0], [11, 45]]], 'day': 6}"

    set schedule for the whole week:

    python smartplug.py -H 172.16.100.75 -l admin -p 1234 -S "[
        {'state': u'ON', 'sched': [[[1, 0], [1, 1]]], 'day': 0},
        {'state': u'ON', 'sched': [[[2, 0], [2, 2]]], 'day': 1},
        {'state': u'ON', 'sched': [[[3, 0], [3, 3]]], 'day': 2},
        {'state': u'ON', 'sched': [[[4, 0], [4, 4]]], 'day': 3},
        {'state': u'ON', 'sched': [[[5, 0], [5, 5]]], 'day': 4},
        {'state': u'ON', 'sched': [[[6, 0], [6, 6]]], 'day': 5},
        {'state': u'ON', 'sched': [[[7, 0], [7, 7]]], 'day': 6},
        ]"

    """

    def __init__(self, host, port, auth):

        """
        Create a new SmartPlug instance identified by the given URL.

        :rtype : object
        :param host: The IP/hostname of the SmartPlug. E.g. '172.16.100.75'
        :param auth: User and password to authenticate with the plug. E.g. ('admin', '1234')
        """

        self.url = "http://%s:%s/smartplug.cgi" % (host, port)
        self.auth = auth
        self.port = port
        self.domi = getDOMImplementation()

    def _xml_cmd_setget_state(self, cmdId, cmdStr):

        """
        Create XML representation of a state command.

        :type self: object
        :type cmdId: str
        :type cmdStr: str
        :rtype: str
        :param cmdId: Use 'get' to request plug state, use 'setup' change plug state.
        :param cmdStr: Empty string for 'get', 'ON' or 'OFF' for 'setup'
        :return: XML representation of command
        """

        doc = self.domi.createDocument(None, "SMARTPLUG", None)
        doc.documentElement.setAttribute("id", "edimax")

        cmd = doc.createElement("CMD")
        cmd.setAttribute("id", cmdId)
        state = doc.createElement("Device.System.Power.State")
        cmd.appendChild(state)
        state.appendChild(doc.createTextNode(cmdStr))

        doc.documentElement.appendChild(cmd)

        return doc.toxml()

    def _xml_cmd_get_sched(self):

        """
        Create XML representation of a command to query schedule of whole week from plug.

        :type self: object
        :rtype: str
        :return: XML representation of command
        """

        doc = self.domi.createDocument(None, "SMARTPLUG", None)
        doc.documentElement.setAttribute("id", "edimax")

        cmd = doc.createElement("CMD")
        cmd.setAttribute("id", "get")
        sched = doc.createElement("SCHEDULE")
        cmd.appendChild(sched)
        state = doc.createElement("Device.System.Power.State")

        doc.documentElement.appendChild(cmd)

        return doc.toxml()

    def _xml_cmd_set_sched(self, sched_days):

        """
        Create XML representation of a command to set scheduling for one day or whole week.

        :type self: object
        :type sched_days: list
        :rtype: str
        :param sched_day: Single day or whole week
        :return: XML representation of command
        """

        doc = self.domi.createDocument(None, "SMARTPLUG", None)
        doc.documentElement.setAttribute("id", "edimax")

        cmd = doc.createElement("CMD")
        cmd.setAttribute("id", "setup")
        sched = doc.createElement("SCHEDULE")
        cmd.appendChild(sched)

        if isinstance(sched_days, list):
            # more then one day

            for one_sched_day in sched_days:

                dev_sched = doc.createElement("Device.System.Power.Schedule.%d" % one_sched_day["day"])
                dev_sched.appendChild(doc.createTextNode(self._render_schedule(one_sched_day["sched"])))
                dev_sched.attributes["value"] = one_sched_day["state"]

                sched.appendChild(dev_sched)

        else:
            # one day
            dev_sched = doc.createElement("Device.System.Power.Schedule.%d" % sched_days["day"])
            dev_sched.appendChild(doc.createTextNode(self._render_schedule(sched_days["sched"])))
            dev_sched.attributes["value"] = sched_days["state"]

            sched.appendChild(dev_sched)

        doc.documentElement.appendChild(cmd)

        return doc.toxml()

    def _post_xml(self, xml):

        """
        Post XML command as multipart file to SmartPlug, parse XML response.

        :type self: object
        :type xml: str
        :rtype: str
        :param xml: XML representation of command (as generated by _xml_cmd)
        :return: 'OK' on success, 'FAILED' otherwise
        """

        files = {'file': xml}

        res = req.post(self.url, auth=self.auth, files=files)

        if res.status_code == req.codes.ok:
            dom = parseString(res.text)

            try:
                val = dom.getElementsByTagName("CMD")[0].firstChild.nodeValue

                if val is None:
                    val = dom.getElementsByTagName("CMD")[0].getElementsByTagName("Device.System.Power.State")[0].\
                        firstChild.nodeValue

                return val

            except Exception as e:

                print(e.__str__())

        return None

    def _post_xml_dom(self, xml):

        """
        Post XML command as multipart file to SmartPlug, return response as raw dom.

        :type self: object
        :type xml: str
        :rtype: object
        :param xml: XML representation of command (as generated by _xml_cmd)
        :return: dom representation of XML response
        """

        files = {'file': xml}

        res = req.post(self.url, auth=self.auth, files=files)

        # print(res.text)

        if res.status_code == req.codes.ok:
            return parseString(res.text)

        return None

    @property
    def state(self):

        """
        Get the current state of the SmartPlug.

        :type self: object
        :rtype: str
        :return: 'ON' or 'OFF'
        """

        res = self._post_xml(self._xml_cmd_setget_state("get", ""))

        if res != "ON" and res != "OFF":
            raise Exception("Failed to communicate with SmartPlug")

        return res

    @state.setter
    def state(self, value):

        """
        Set the state of the SmartPlug

        :type self: object
        :type value: str
        :param value: 'ON', 'on', 'OFF' or 'off'
        """

        if value == "ON" or value == "on":
            res = self._post_xml(self._xml_cmd_setget_state("setup", "ON"))
        else:
            res = self._post_xml(self._xml_cmd_setget_state("setup", "OFF"))

        if res != "OK":
            raise Exception("Failed to communicate with SmartPlug")

    def _parse_schedule(self, sched):

        """
        Parse the plugs internal scheduling format string to python array

        :type self: object
        :type sched: str
        :rtype: list
        :param sched: scheduling string (of one day) as returned by plug
        :return: python array with scheduling: [[[start_hh:start_mm],[end_hh:end_mm]], ... ]
        """

        sched_unpacked = [0] * 60 * 24
        hours = []

        idx_sched = 0

        # first, unpack the packed schedule from the plug
        for packed in sched:

            int_packed = int(packed, 16)

            sched_unpacked[idx_sched+0] = (int_packed >> 3) & 1
            sched_unpacked[idx_sched+1] = (int_packed >> 2) & 1
            sched_unpacked[idx_sched+2] = (int_packed >> 1) & 1
            sched_unpacked[idx_sched+3] = (int_packed >> 0) & 1

            idx_sched += 4

        idx_hours = 0

        hour = 0
        min = 0

        found_range = False

        # second build time array from unpacked schedule
        for m in sched_unpacked:

            if m == 1 and not found_range:
                found_range = True
                hours.append([[hour, min], [23, 59]])

            elif m == 0 and found_range:
                found_range = False
                hours[idx_hours][1][0] = hour
                hours[idx_hours][1][1] = min
                idx_hours += 1

            min += 1

            if min > 59:
                min = 0
                hour += 1

        return hours

    def _render_schedule(self, hours):

        """
        Render python scheduling array back to plugs internal format

        :type self: object
        :type hours: list
        :rtype: str
        :param hours: python array with scheduling hours: [[[start_hh:start_mm],[end_hh:end_mm]], ... ]
        :return: scheduling string (of one day) as needed by plug
        """

        sched = [0] * 60 * 24
        sched_str = ''

        # first, set every minute we found a schedule to 1 in the sched array
        for times in hours:

            idx_start = times[0][0] * 60 + times[0][1]
            idx_end = times[1][0] * 60 + times[1][1]

            if idx_end < idx_start:
                idx_end = 60 * 24

            for i in range(idx_start, idx_end):
                sched[i] = 1

        # second, pack the minute array from above into the plug format and make a string out of it
        for i in range(0, 60 * 24, 4):
            packed = (sched[i] << 3) + (sched[i+1] << 2) + (sched[i+2] << 1) + (sched[i+3] << 0)
            sched_str += "%X" % packed

        return sched_str

    @property
    def schedule(self):

        """
        Get scheduling for all days of week from plug as python list.
        Note: it looks like the plug only is able to return a whole week.

        :type self: object
        :rtype: list
        :return: List with scheduling for each day of week:

        [
        {'state': u'ON|OFF', 'sched': [[[hh, mm], [hh, mm]], ...], 'day': 0..6},
        ...
        ]
        """

        sched = []

        dom = self._post_xml_dom(self._xml_cmd_get_sched())

        if dom is None:
            return sched

        try:

            dom_sched = dom.getElementsByTagName("CMD")[0].getElementsByTagName("SCHEDULE")[0]

            for i in range(0, 7):

                sched.append(
                    {"day": i,
                     "state": dom_sched.getElementsByTagName("Device.System.Power.Schedule.%d" % i)[0].attributes["value"].
                            firstChild.nodeValue,
                     "sched": self._parse_schedule(dom_sched.getElementsByTagName("Device.System.Power.Schedule.%d" % i)[0].
                            firstChild.nodeValue)})

        except Exception as e:

            print(e.__str__())

        return sched

    @schedule.setter
    def schedule(self, sched):

        """
        Set scheduling for ony day of week or for whole week on the plug.
        Note: it seams not to be possible to schedule anything else then one day or a whole week.

        :type self: object
        :type sched: list
        :rtype: str
        :param sched: Array with scheduling hours for ons day:

                        {'day': 0..6, 'state': 'ON' | 'OFF', [[start_hh:start_mm],[end_hh:end_mm]], ... ]}

                      Or whole week:

                        [{'day': 0..6, 'state': 'ON' | 'OFF', [[start_hh:start_mm],[end_hh:end_mm]], ... ]}, ...]

        :return: 'OK' (or exception on error)
        """

        res = self._post_xml(self._xml_cmd_set_sched(sched))

        if res != "OK":
            raise Exception("Failed to communicate with SmartPlug")

        return res

if __name__ == "__main__":

    # this turns on debugging from requests library
    log.basicConfig(level=log.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

    usage = "%prog [options]"

    parser = par.OptionParser(usage)

    parser.add_option("-H", "--host",  default="172.16.100.75", help="Base URL of the SmartPlug")
    parser.add_option("-C", "--port",  default="10000", help="Port to connect with SmartPlug")
    parser.add_option("-l", "--login",  default="admin", help="Login user to authenticate with SmartPlug")
    parser.add_option("-p", "--password",  default="1234", help="Password to authenticate with SmartPlug")

    parser.add_option("-g", "--get",  action="store_true", help="Get state of plug")
    parser.add_option("-s", "--set",  help="Set state of plug: ON or OFF")

    parser.add_option("-G", "--getsched", action="store_true", help="Get schedule from Plug")
    parser.add_option("-P", "--getschedpy", action="store_true", help="Get schedule from Plug as Python list")
    parser.add_option("-S", "--setsched", help="Set schedule of Plug")

    (options, args) = parser.parse_args()

    p = SmartPlug(options.host, options.port, (options.login, options.password))

    if options.get:

        print(p.state)

    elif options.set:

        p.state = options.set

    elif options.getsched:

        days = { 0 : "Sunday", 1 : "Monday", 2 : "Tuesday", 3 : "Wednesday",
                 4 : "Thursday", 5 : "Friday", 6 : "Saturday"}

        for day in p.schedule:

            if len(day["sched"]) > 0:
                print("Schedules for: %s (%s)" % (days[day["day"]], day["state"]))

            for sched in day["sched"]:
                print(" * %02d:%02d - %02d:%02d" % (sched[0][0], sched[0][1], sched[1][0], sched[1][1]))

    elif options.getschedpy:

        # print(p.schedule.__str__().replace("{", "\n{").replace("}]", "}\n]"))
        print(p.schedule.__str__())

    elif options.setsched:

        try:

            sched = eval(options.setsched)
            p.schedule = sched

        except Exception as e:

            print("Wrong input format: %s" % e.__str__())
            exit(-1)
