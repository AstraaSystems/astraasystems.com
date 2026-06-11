#!/usr/bin/env python3
#===============================================================================
#  ARDHANARISHVARA OS KERNEL MODULE
#  SovereignOS Desktop Shell — Windowing, Panels, Dock & UI Orchestration Layer
#  File: sovereign_desktop_shell.py
#===============================================================================

import time
import uuid
from typing import Dict, Any, List, Optional

class SovereignDesktopShell:
    """
    Provides:
      • desktop environment orchestration
      • panel & dock management
      • wallpaper engine
      • workspace switching
      • window manager integration
      • kernel-driven UI shell state
    """

    def __init__(self, window_manager):
        self.window_manager = window_manager
        self.workspaces: Dict[int, List[str]] = {1: []}
        self.active_workspace = 1
        self.wallpaper = "#000000"
        self.panels: Dict[str, Dict[str, Any]] = {}
        self.dock: List[str] = []

    #---------------------------------------------------------------------------
    #  SET WALLPAPER
    #---------------------------------------------------------------------------
    def set_wallpaper(self, color_or_path: str):
        self.wallpaper = color_or_path

    #---------------------------------------------------------------------------
    #  REGISTER PANEL
    #---------------------------------------------------------------------------
    def register_panel(self, name: str, config: Dict[str, Any]):
        self.panels[name] = config

    #---------------------------------------------------------------------------
    #  ADD TO DOCK
    #---------------------------------------------------------------------------
    def dock_add(self, app_id: str):
        if app_id not in self.dock:
            self.dock.append(app_id)

    #---------------------------------------------------------------------------
    #  REMOVE FROM DOCK
    #---------------------------------------------------------------------------
    def dock_remove(self, app_id: str):
        if app_id in self.dock:
            self.dock.remove(app_id)

    #---------------------------------------------------------------------------
    #  CREATE WORKSPACE
    #---------------------------------------------------------------------------
    def create_workspace(self, index: int):
        if index not in self.workspaces:
            self.workspaces[index] = []

    #---------------------------------------------------------------------------
    #  SWITCH WORKSPACE
    #---------------------------------------------------------------------------
    def switch_workspace(self, index: int):
        if index not in self.workspaces:
            return False

        self.active_workspace = index
        return True

    #---------------------------------------------------------------------------
    #  OPEN WINDOW IN WORKSPACE
    #---------------------------------------------------------------------------
    def open_window(self, title: str, x: int, y: int, w: int, h: int) -> str:
        win = self.window_manager.create(title, x, y, w, h)
        wid = win["id"]
        self.workspaces[self.active_workspace].append(wid)
        return wid

    #---------------------------------------------------------------------------
    #  CLOSE WINDOW
    #---------------------------------------------------------------------------
    def close_window(self, wid: str):
        for ws in self.workspaces.values():
            if wid in ws:
                ws.remove(wid)
        self.window_manager.close(wid)

    #---------------------------------------------------------------------------
    #  DESKTOP SNAPSHOT
    #---------------------------------------------------------------------------
    def snapshot(self) -> Dict[str, Any]:
        return {
            "shell_id": f"SHL-{uuid.uuid4().hex[:10].upper()}",
            "timestamp": time.time(),
            "active_workspace": self.active_workspace,
            "workspaces": self.workspaces,
            "wallpaper": self.wallpaper,
            "panels": self.panels,
            "dock": self.dock,
            "window_manager": self.window_manager.snapshot()
        }

#===============================================================================
#  END OF FILE — sovereign_desktop_shell.py
#===============================================================================
