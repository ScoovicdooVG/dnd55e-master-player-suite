import json
import socket
import threading
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from PIL import Image
import qrcode

from database.db_manager import DatabaseManager
from models.character_55e import (
    Character55eRules, ABILITIES, SKILLS_55E, WEAPON_MASTERIES_55E,
    SPECIES_55E, BACKGROUNDS_55E, CLASSES_55E, ARMORS_CATALOG_55E,
    WEAPONS_CATALOG_55E, PACK_CONTENTS_55E, MOUNTS_CAPACITY_KG,
    SPELLS_CATALOG_55E, ITEMS_CATALOG_BY_CATEGORY, LANGUAGES_55E,
    MUSICAL_INSTRUMENTS, GAMING_SETS, SPECIES_LINEAGES_55E,
    ELD_INVOCATIONS_55E, FIGHTING_STYLES_55E, GENERAL_FEATS_55E,
    EPIC_BOONS_55E, XP_THRESHOLDS_55E, TAVERN_AND_SERVICES_55E,
    MAGIC_ITEMS_ATTUNEMENT_55E
)


MOBILE_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>D&D 5.5e Suite Móvil</title>
<style>
  :root {
    --bg: #0b1120; --card: #1e293b; --card-alt: #0f172a;
    --accent: #2563eb; --gold: #fbbf24; --green: #10b981;
    --red: #ef4444; --purple: #7c3aed; --orange: #d97706;
    --text: #f8fafc; --muted: #94a3b8; --border: #334155;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
  body { background: var(--bg); color: var(--text); padding: 10px; padding-bottom: 80px; }
  h1 { font-size: 1.15rem; color: var(--gold); margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
  select, input, textarea, button {
    background: #1e293b; color: white; border: 1px solid var(--border);
    padding: 9px 10px; border-radius: 8px; font-size: 0.92rem; width: 100%;
  }
  textarea { resize: vertical; min-height: 220px; line-height: 1.45; }
  button { background: var(--accent); border: none; font-weight: bold; cursor: pointer; }
  button:active { opacity: 0.8; }
  label { font-size: 0.78rem; color: var(--muted); font-weight: bold; display: block; margin-top: 8px; margin-bottom: 3px; }
  .card { background: var(--card); border-radius: 10px; padding: 12px; margin-bottom: 10px; border: 1px solid var(--border); }
  .grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; text-align: center; }
  .grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
  .stat-box { background: var(--card-alt); padding: 8px 4px; border-radius: 8px; border: 1px solid var(--border); }
  .stat-box .val { font-size: 1.15rem; font-weight: bold; color: var(--gold); }
  .stat-box .lbl { font-size: 0.7rem; color: var(--muted); text-transform: uppercase; }
  .tabs { display: flex; gap: 5px; overflow-x: auto; margin-bottom: 10px; padding-bottom: 4px; }
  .tab-btn {
    background: var(--card); color: var(--muted); padding: 9px 11px;
    border-radius: 8px; font-size: 0.8rem; white-space: nowrap; width: auto; border: 1px solid var(--border);
  }
  .tab-btn.active { background: #8B2635; color: white; border-color: #f87171; }
  .row-item { display: flex; justify-content: space-between; align-items: center; padding: 7px 0; border-bottom: 1px solid var(--border); font-size: 0.88rem; gap: 6px; }
  .badge { color: var(--green); font-weight: bold; }
  .sub-note { font-size: 0.78rem; color: var(--muted); margin-top: 2px; }
  .alert-row { display: flex; align-items: center; gap: 8px; margin-top: 6px; }
  .status-icon { font-weight: bold; font-size: 0.85rem; width: 26px; text-align: center; padding: 4px; border-radius: 6px; }
  .status-warn { background: rgba(239,68,68,0.2); color: var(--red); }
  .status-ok { background: rgba(16,185,129,0.2); color: var(--green); }
  .slot-pill { display: inline-flex; align-items: center; gap: 4px; background: var(--card-alt); padding: 6px 10px; border-radius: 6px; border: 1px solid var(--border); margin: 3px; font-size: 0.82rem; }
  .cont-header { background: #334155; padding: 8px 10px; border-radius: 6px; font-weight: bold; display: flex; justify-content: space-between; align-items: center; cursor: pointer; margin-top: 6px; }
  .cont-body { background: var(--card-alt); padding: 6px 10px; border-left: 3px solid var(--accent); margin-bottom: 6px; border-radius: 0 0 6px 6px; }
  .btn-sm { width: auto; padding: 5px 9px; font-size: 0.76rem; border-radius: 6px; }
  pre { white-space: pre-wrap; font-size: 0.84rem; line-height: 1.45; color: #e2e8f0; }
</style>
</head>
<body>
  <h1>
    <span>🐉 D&D 5.5e Suite Móvil</span>
    <button class="btn-sm" onclick="fetchCharacters(currentCharId)" style="background:#334155;">↻ Sincronizar</button>
  </h1>

  <div class="card" style="display:flex;gap:6px;align-items:center;padding:8px;">
    <select id="charSelect" onchange="loadCharDetail()" style="flex:1;">
      <option value="">Cargando héroes...</option>
    </select>
    <button class="btn-sm" onclick="startBlankCharacterInShard()" style="background:var(--green);padding:9px 11px;">+ Nuevo</button>
  </div>

  <div class="tabs">
    <button class="tab-btn active" id="btnTabSheet" onclick="showTab('tabSheet', this)">🛡️ Combate</button>
    <button class="tab-btn" id="btnTabLive" onclick="showTab('tabLive', this);loadLiveTableMobile();">🗺️ Mesa en Vivo</button>
    <button class="tab-btn" id="btnTabShard" onclick="showTab('tabShard', this)">⚙️ Shard (1-20)</button>
    <button class="tab-btn" id="btnTabSpells" onclick="showTab('tabSpells', this)">✨ Conjuros</button>
    <button class="tab-btn" id="btnTabInv" onclick="showTab('tabInv', this)">🎒 Equipo</button>
    <button class="tab-btn" id="btnTabShop" onclick="showTab('tabShop', this);loadMobileShop();">🏪 Tienda</button>
    <button class="tab-btn" id="btnTabSkills" onclick="showTab('tabSkills', this)">🎯 Habilidades</button>
    <button class="tab-btn" id="btnTabFeatures" onclick="showTab('tabFeatures', this)">📜 Rasgos</button>
    <button class="tab-btn" id="btnTabNotes" onclick="showTab('tabNotes', this)">📝 Notas</button>
    <button class="tab-btn" id="btnTabPdf" onclick="showTab('tabPdf', this)">📖 PDF</button>
  </div>

  <!-- PESTAÑA 1: HOJA DE COMBATE -->
  <div id="tabSheet" class="tab-pane">
    <div class="card" id="headerInfo">Selecciona un héroe arriba o toca "+ Nuevo" para crear uno con opciones Shard.</div>

    <div class="card">
      <div class="grid-3" style="margin-bottom:8px;">
        <div class="stat-box"><div class="lbl">CA</div><div class="val" id="acVal">-</div></div>
        <div class="stat-box"><div class="lbl">Iniciativa</div><div class="val" id="initVal" style="color:var(--green);">-</div></div>
        <div class="stat-box"><div class="lbl">Velocidad</div><div class="val" id="spdVal">-</div></div>
      </div>

      <div class="grid-3" style="margin-bottom:8px;">
        <div class="stat-box"><div class="lbl">PG Actuales</div><input id="hpCurrInput" type="number" style="text-align:center;font-weight:bold;margin-top:3px;"></div>
        <div class="stat-box"><div class="lbl">PG Máximos</div><input id="hpMaxInput" type="number" style="text-align:center;font-weight:bold;margin-top:3px;"></div>
        <div class="stat-box"><div class="lbl">PG Temp.</div><input id="hpTempInput" type="number" style="text-align:center;margin-top:3px;"></div>
      </div>

      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;font-size:0.84rem;">
        <span id="hitDiceLbl" style="color:var(--green);font-weight:bold;">🎲 Dados de Golpe: 1/1</span>
        <label style="margin:0;display:flex;align-items:center;gap:5px;color:var(--gold);">
          <input type="checkbox" id="inspCheck" style="width:18px;height:18px;"> Inspiración Heroica
        </label>
      </div>

      <div class="grid-3" style="margin-bottom:8px;">
        <button onclick="openShortRestPrompt()" style="background:#065f46;font-size:0.8rem;padding:8px 4px;">⛺ Desc. Corto</button>
        <button onclick="takeLongRestMobile()" style="background:#1e3a8a;font-size:0.8rem;padding:8px 4px;">🌙 Desc. Largo</button>
        <button onclick="openLevelUpPrompt()" style="background:var(--orange);font-size:0.8rem;padding:8px 4px;">⬆️ Subir Nivel</button>
      </div>

      <button onclick="saveCombatAndEquipment()" style="background:var(--green);width:100%;">💾 Guardar Estado de Combate</button>
    </div>

    <div class="card">
      <div style="font-weight:bold;color:var(--gold);margin-bottom:6px;">🛡️ Armadura Equipada (Cálculo Automático CA)</div>
      <select id="eqArmorSelect" onchange="saveCombatAndEquipment()"></select>
      <div class="grid-2" style="margin-top:6px;align-items:center;">
        <label style="margin:0;display:flex;align-items:center;gap:6px;color:var(--text);">
          <input type="checkbox" id="eqShieldCheck" onchange="saveCombatAndEquipment()" style="width:18px;height:18px;"> Escudo (+2 CA)
        </label>
        <div style="display:flex;align-items:center;gap:6px;">
          <span class="sub-note" style="white-space:nowrap;">Bono Mágico CA:</span>
          <input type="number" id="eqAcBonus" value="0" onchange="saveCombatAndEquipment()" style="text-align:center;">
        </div>
      </div>
    </div>

    <div class="card">
      <div style="font-weight:bold;color:var(--gold);margin-bottom:6px;">⚔️ Armas Equipadas y Maestrías (Metros)</div>
      <div id="weaponsEditorContainer"></div>
      <button onclick="saveCombatAndEquipment()" style="margin-top:8px;background:var(--accent);">Actualizar Armas Equipadas</button>
    </div>

    <div class="card">
      <div style="font-weight:bold;margin-bottom:8px;color:var(--gold);">Características y Salvaciones</div>
      <div class="grid-3" id="abilitiesGrid"></div>
    </div>
  </div>

  <!-- PESTAÑA MESA EN VIVO: MAPAS/HANDOUTS, AMBIENTE E INICIATIVA DEL ENCUENTRO -->
  <div id="tabLive" class="tab-pane" style="display:none;">
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <span style="font-weight:bold;color:var(--gold);font-size:1.05rem;">🗺️ Mesa en Vivo del DM</span>
        <button class="btn-sm" onclick="loadLiveTableMobile()" style="background:#334155;">↻ Actualizar Vista</button>
      </div>
      <div id="liveEnvBanner" style="margin-top:8px;padding:8px;background:var(--card-alt);border-radius:8px;border:1px solid var(--border);font-size:0.82rem;"></div>
    </div>

    <!-- Orden de Iniciativa en Vivo (Con Niebla de Guerra) -->
    <div class="card">
      <div style="font-weight:bold;color:var(--green);margin-bottom:6px;" id="liveCombatHeader">⚔️ Rastreador de Iniciativa de la Mesa</div>
      <div id="liveCombatList">No hay un combate activo en este momento.</div>
    </div>

    <!-- Visor de Mapa / Handout Proyectado por el DM -->
    <div class="card">
      <div style="font-weight:bold;color:#a78bfa;margin-bottom:4px;" id="liveHandoutTitle">🖼️ Proyector de Mapas y Pistas</div>
      <div class="sub-note" id="liveHandoutCaption" style="margin-bottom:8px;"></div>
      <div id="liveHandoutImgBox" style="text-align:center;"></div>
    </div>
  </div>

  <!-- PESTAÑA 2: OPCIONES SHARD ACUMULATIVAS -->
  <div id="tabShard" class="tab-pane" style="display:none;">
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <div style="font-size:1.05rem;font-weight:bold;color:var(--gold);" id="shardHeaderTitle">Opciones Shard (Niveles 1 a N)</div>
        <span id="shardSuggestedHp" class="badge"></span>
      </div>
      <div class="sub-note" style="margin-bottom:8px;">
        Si estás en Nivel 1 verás las opciones de Nivel 1. Al cambiar el Nivel aquí abajo, aparecerán todas las opciones acumuladas de tu clase y subclase hasta ese nivel.
      </div>

      <div class="grid-2">
        <div><label>Nombre del Héroe</label><input id="sh_name" placeholder="Ej. Valerius"></div>
        <div><label>Jugador</label><input id="sh_player" placeholder="Tu nombre"></div>
      </div>

      <div class="grid-2">
        <div><label>Especie (5.5e)</label><select id="sh_species" onchange="rebuildShardProgressiveOptions()"></select></div>
        <div><label>Trasfondo (2024)</label><select id="sh_bg" onchange="rebuildShardProgressiveOptions()"></select></div>
      </div>

      <div class="grid-2">
        <div><label>Clase</label><select id="sh_class" onchange="rebuildShardProgressiveOptions()"></select></div>
        <div>
          <label>Nivel Actual (1-20)</label>
          <select id="sh_level" onchange="rebuildShardProgressiveOptions()"></select>
        </div>
      </div>

      <div class="grid-2" style="margin-top:4px;">
        <div><label>XP Actual</label><input id="sh_xp" type="number" value="0"></div>
        <div><label>Dote de Origen (Trasfondo)</label><input id="sh_origin_feat" readonly style="opacity:0.85;"></div>
      </div>
    </div>

    <div class="card">
      <div style="font-weight:bold;color:var(--gold);margin-bottom:4px;">NIVEL 1 — Puntuaciones Base (Antes de Trasfondo/Mejoras)</div>
      <div class="grid-3" id="shardBaseScoresGrid"></div>
      <button class="btn-sm" onclick="applyStdArrayInShard()" style="margin-top:8px;width:100%;background:#334155;">
        Aplicar Conjunto Estándar de la Clase (15, 14, 13, 12, 10, 8)
      </button>
    </div>

    <div id="shardDynamicLevelsContainer"></div>

    <button onclick="saveShardProgressionFromMobile()" style="background:var(--green);padding:13px;font-size:1rem;width:100%;">
      ✔ Guardar Personaje y Aplicar Progresión Shard
    </button>
  </div>

  <!-- PESTAÑA 3: CONJUROS -->
  <div id="tabSpells" class="tab-pane" style="display:none;">
    <div class="card">
      <div style="font-weight:bold;color:var(--gold);margin-bottom:4px;" id="spellStatsBanner">Aptitud Mágica</div>
      <div id="spellSlotsTracker" style="margin-top:6px;"></div>
      <div id="alwaysPreparedBox" class="sub-note" style="color:var(--green);margin-top:6px;"></div>
    </div>

    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="font-weight:bold;color:var(--gold);" id="spellCountersLabel">Trucos: 0/0 | Preparados: 0/0</span>
        <label style="margin:0;display:flex;align-items:center;gap:4px;font-size:0.78rem;">
          <input type="checkbox" id="chkOnlyMyClassSpells" checked onchange="renderMobileSpellPicker()" style="width:16px;height:16px;"> Solo mi clase
        </label>
      </div>
      <input id="spellSearchInput" placeholder="Filtrar conjuro por nombre o escuela..." oninput="renderMobileSpellPicker()" style="margin-bottom:8px;">
      <div id="spellPickerList" style="max-height:380px;overflow-y:auto;"></div>
      <button onclick="saveSelectedSpellsMobile()" style="margin-top:10px;background:var(--purple);">💾 Guardar Conjuros Preparados</button>
    </div>

    <div class="card" id="spellPdfPreviewCard" style="display:none;">
      <div style="font-weight:bold;color:var(--gold);margin-bottom:4px;">📖 Descripción en el Manual PDF</div>
      <div id="spellPdfPreviewText" class="sub-note" style="color:var(--text);"></div>
    </div>
  </div>

  <!-- PESTAÑA 4: EQUIPAMIENTO, SINTONIZACIÓN Y MONTURA -->
  <div id="tabInv" class="tab-pane" style="display:none;">
    <!-- Monedero -->
    <div class="card">
      <div style="font-weight:bold;margin-bottom:6px;color:var(--gold);">💰 Monedero del Jugador</div>
      <div class="grid-3">
        <div><span class="sub-note">Cobre (PC)</span><input id="cpInput" type="number"></div>
        <div><span class="sub-note">Plata (PP)</span><input id="spInput" type="number"></div>
        <div><span class="sub-note">Oro (PO)</span><input id="gpInput" type="number"></div>
      </div>
      <button onclick="saveCombatAndEquipment()" style="margin-top:8px;background:#059669;">Guardar Monedas</button>
    </div>

    <!-- Sintonización con Objetos Mágicos (Máx 3 - Pág. 232) -->
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
        <span style="font-weight:bold;color:#a78bfa;">✨ Sintonización con Objetos Mágicos</span>
        <span class="sub-note" id="attuneCountBadge">0 / 3 sintonizados</span>
      </div>
      <div class="sub-note" style="margin-bottom:6px;">Máximo 3 objetos mágicos sintonizados a la vez y sin copias duplicadas (Pág. 232).</div>
      <select id="attuneSlot0" onchange="saveAttunementMobile(0)" style="margin-bottom:5px;"></select>
      <select id="attuneSlot1" onchange="saveAttunementMobile(1)" style="margin-bottom:5px;"></select>
      <select id="attuneSlot2" onchange="saveAttunementMobile(2)"></select>
    </div>

    <!-- Buscador del Catálogo Oficial Cap. 6 (Gratis / Manual) -->
    <div class="card">
      <div style="font-weight:bold;color:var(--gold);margin-bottom:6px;">🔍 Tomar del Catálogo (Sin costo / Botín)</div>
      <div class="grid-2" style="margin-bottom:6px;">
        <div>
          <label style="margin-top:0;">Categoría</label>
          <select id="catCategorySelect" onchange="renderMobileItemCatalog()"></select>
        </div>
        <div>
          <label style="margin-top:0;">Enviar a</label>
          <select id="catDestSelect"></select>
        </div>
      </div>
      <div style="display:flex;gap:6px;margin-bottom:6px;">
        <input id="catSearchInput" placeholder="Buscar objeto (ej. Mochila, Paquete, Poción)..." oninput="renderMobileItemCatalog()" style="flex:1;">
        <input id="catQtyInput" type="number" value="1" min="1" style="width:65px;text-align:center;">
      </div>
      <div id="catItemsScroll" style="max-height:190px;overflow-y:auto;border:1px solid var(--border);border-radius:8px;padding:6px;background:var(--card-alt);"></div>
    </div>

    <!-- Objeto Personalizado -->
    <div class="card">
      <div style="font-weight:bold;color:var(--muted);font-size:0.85rem;margin-bottom:4px;">+ Objeto Personalizado Rápido</div>
      <div style="display:flex;gap:4px;margin-bottom:6px;">
        <input id="custItemName" placeholder="Nombre del objeto" style="flex:2;">
        <input id="custItemQty" type="number" value="1" placeholder="Cant" style="width:55px;text-align:center;">
        <input id="custItemKg" type="number" step="0.1" value="0.5" placeholder="kg" style="width:65px;text-align:center;">
      </div>
      <div style="display:flex;justify-content:space-between;align-items:center;gap:6px;">
        <label style="margin:0;display:flex;align-items:center;gap:5px;color:var(--text);">
          <input type="checkbox" id="custItemIsCont" style="width:16px;height:16px;"> Contenedor Desplegable
        </label>
        <button class="btn-sm" onclick="addCustomItemMobile('char')" style="background:var(--accent);">+ Al PJ</button>
        <button class="btn-sm" onclick="addCustomItemMobile('mount')" style="background:var(--orange);">+ A Montura</button>
      </div>
    </div>

    <!-- Inventario del Personaje -->
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="font-weight:bold;color:var(--green);">🎒 Inventario del Personaje</span>
        <span id="charWeightBadge" class="badge">0.0 / 75.0 kg</span>
      </div>
      <div class="sub-note" style="margin-bottom:6px;">Usa "💰 50%" para vender equipo a mitad de su precio oficial (Pág. 213).</div>
      <div id="charInvContainer"></div>
    </div>

    <!-- Inventario de la Montura -->
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
        <span style="font-weight:bold;color:#60a5fa;">🫏 Montura / Vehículo</span>
        <span id="mountWeightBadge" style="color:#60a5fa;font-weight:bold;font-size:0.85rem;">0.0 / 0.0 kg</span>
      </div>
      <select id="mountTypeSelect" onchange="changeMountTypeMobile()" style="margin-bottom:8px;"></select>
      <div id="mountInvContainer"></div>
    </div>
  </div>

  <!-- ==================================================================== -->
  <!-- PESTAÑA 5: TIENDA Y TABERNA EN VIVO DEL DM (COMPRA AUTOMÁTICA)       -->
  <!-- ==================================================================== -->
  <div id="tabShop" class="tab-pane" style="display:none;">
    <div class="card">
      <div style="display:flex;justify-content:space-between;align-items:center;">
        <div style="font-size:1.1rem;font-weight:bold;color:var(--gold);" id="shopHeaderName">🏪 Tienda del Pueblo</div>
        <button class="btn-sm" onclick="loadMobileShop()" style="background:#334155;">↻ Actualizar</button>
      </div>
      <div class="sub-note" id="shopPresetSubtitle">Catálogo del DM</div>
      <div style="margin-top:8px;padding:8px;background:var(--card-alt);border-radius:8px;border:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">
        <span class="sub-note">Tu Monedero Actual:</span>
        <span id="shopPlayerWallet" style="font-weight:bold;color:var(--gold);">0 PO | 0 PP | 0 PC</span>
      </div>

      <div class="grid-2" style="margin-top:8px;">
        <div>
          <label style="margin-top:0;">Guardar compra en:</label>
          <select id="shopBuyDestSelect">
            <option value="char">🎒 Mi Inventario Personal</option>
            <option value="mount">🫏 Inventario de mi Montura</option>
          </select>
        </div>
        <div>
          <label style="margin-top:0;">Cantidad a comprar:</label>
          <input id="shopBuyQty" type="number" value="1" min="1" style="text-align:center;">
        </div>
      </div>

      <input id="shopSearchInput" placeholder="Buscar artículo en la tienda (ej. Cerveza, Poción, Coraza, Cuerda)..." oninput="renderShopCatalogMobile()" style="margin-top:8px;">
    </div>

    <div class="card" id="shopCatalogContainer">Cargando artículos de la tienda...</div>
  </div>

  <!-- PESTAÑA 6: HABILIDADES -->
  <div id="tabSkills" class="tab-pane" style="display:none;">
    <div class="card" id="passivesBanner" style="color:var(--gold);font-weight:bold;text-align:center;"></div>
    <div class="card" id="skillsList"></div>
  </div>

  <!-- PESTAÑA 7: RASGOS -->
  <div id="tabFeatures" class="tab-pane" style="display:none;">
    <div class="card"><pre id="featuresText"></pre></div>
  </div>

  <!-- PESTAÑA 8: NOTAS DEL JUGADOR -->
  <div id="tabNotes" class="tab-pane" style="display:none;">
    <div class="card">
      <div style="font-weight:bold;color:var(--gold);margin-bottom:6px;">📝 Diario y Notas de Aventura del Jugador</div>
      <div class="sub-note" style="margin-bottom:8px;">Escribe aquí tus apuntes de sesión, pistas, nombres de PNJs, misiones o historia de tu personaje.</div>
      <textarea id="adventureNotesArea" placeholder="Escribe tus notas de aventura aquí..."></textarea>
      <button onclick="saveAdventureNotesMobile()" style="margin-top:10px;background:var(--green);">💾 Guardar Notas en la PC del DM</button>
    </div>
  </div>

  <!-- PESTAÑA 9: BUSCADOR PDF -->
  <div id="tabPdf" class="tab-pane" style="display:none;">
    <div class="card">
      <div style="display:flex;gap:6px;margin-bottom:10px;">
        <input id="pdfQuery" placeholder="Buscar conjuro, dote o regla en los PDFs..." style="flex:1;">
        <button onclick="searchPdf()" style="width:auto;padding:9px 14px;">Buscar</button>
      </div>
      <div id="pdfResults">Escribe cualquier término para consultar los manuales PDF indexados en la PC del DM.</div>
    </div>
  </div>

<script>
let currentCharId = null;
let charData = null;
let catalogs = null;
let currentShopData = null;

function showTab(tabId, btn) {
  document.querySelectorAll('.tab-pane').forEach(el => el.style.display = 'none');
  document.getElementById(tabId).style.display = 'block';
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  btn.classList.add('active');
}

async function initCatalogs() {
  try {
    const res = await fetch('/api/catalogs');
    catalogs = await res.json();

    const fill = (id, arr) => {
      const el = document.getElementById(id);
      if (!el) return;
      el.innerHTML = arr.map(v => `<option value="${v}">${v}</option>`).join('');
    };

    fill('sh_species', Object.keys(catalogs.species_full));
    fill('sh_bg', Object.keys(catalogs.backgrounds_full));
    fill('sh_class', Object.keys(catalogs.classes_full));
    fill('sh_level', Array.from({length: 20}, (_, i) => String(i + 1)));
    fill('eqArmorSelect', catalogs.armors);
    fill('mountTypeSelect', Object.keys(catalogs.mounts));
    fill('catCategorySelect', ['Todas las Categorías', ...Object.keys(catalogs.items_by_cat)]);

    const attOpts = ['-- Ranura Libre --', ...(catalogs.magic_attune || [])];
    fill('attuneSlot0', attOpts);
    fill('attuneSlot1', attOpts);
    fill('attuneSlot2', attOpts);

    const baseGrid = document.getElementById('shardBaseScoresGrid');
    baseGrid.innerHTML = catalogs.abilities.map(ab => `
      <div class="stat-box">
        <div class="lbl">${ab.slice(0,3)}</div>
        <input type="number" id="sh_base_${ab}" value="10" min="1" max="20" style="text-align:center;font-weight:bold;margin-top:3px;" onchange="updateShardSuggestedHp()">
      </div>
    `).join('');

    renderMobileItemCatalog();
  } catch (err) {
    alert('Error cargando catálogos: ' + err);
  }
}

async function fetchCharacters(selectId = null) {
  try {
    const res = await fetch('/api/characters');
    const list = await res.json();
    const sel = document.getElementById('charSelect');
    const prev = selectId !== null ? String(selectId) : sel.value;

    if (!list || list.length === 0) {
      sel.innerHTML = '<option value="">-- Sin personajes guardados (Toca + Nuevo) --</option>';
      startBlankCharacterInShard();
      return;
    }

    sel.innerHTML = '<option value="">-- Selecciona tu Héroe --</option>';
    list.forEach(c => {
      const opt = document.createElement('option');
      opt.value = String(c.id);
      opt.textContent = `${c.name} — Niv. ${c.level} ${c.species} ${c.char_class}`;
      sel.appendChild(opt);
    });

    if (prev && list.some(x => String(x.id) === prev)) {
      sel.value = prev;
      await loadCharDetail();
    } else {
      sel.value = String(list[0].id);
      await loadCharDetail();
    }
  } catch (err) {
    alert('Error al obtener personajes: ' + err);
  }
}

async function loadCharDetail() {
  const cid = document.getElementById('charSelect').value;
  if (!cid) return;
  currentCharId = parseInt(cid);
  const res = await fetch(`/api/character?id=${cid}`);
  charData = await res.json();
  renderAllMobileViews();
}

function renderAllMobileViews() {
  if (!charData || !catalogs) return;
  const d = charData;
  const st = d.stats || {};

  document.getElementById('headerInfo').innerHTML = `
    <div style="font-size:1.15rem;font-weight:bold;">${d.name} <span style="color:var(--gold);">(Nivel ${d.level})</span></div>
    <div class="sub-note">${d.species} • ${d.char_class} (${d.subclass}) • Trasfondo: ${d.background}</div>
    <div class="sub-note" style="color:#60a5fa;margin-top:4px;">Competencia: +${d.prof} | XP: ${d.xp_current.toLocaleString()} / ${d.xp_next.toLocaleString()} | Dote Origen: ${st.origin_feat || '—'}</div>
  `;

  document.getElementById('acVal').textContent = d.ac;
  document.getElementById('initVal').textContent = d.init;
  document.getElementById('spdVal').textContent = d.speed;
  document.getElementById('hpCurrInput').value = d.hp_curr;
  document.getElementById('hpMaxInput').value = d.hp_max;
  document.getElementById('hpTempInput').value = d.hp_temp;
  document.getElementById('hitDiceLbl').textContent = `🎲 Dados de Golpe: ${d.hit_dice} d${d.hit_die_faces}`;
  document.getElementById('inspCheck').checked = !!st.heroic_inspiration;

  document.getElementById('eqArmorSelect').value = st.equipped_armor || 'Sin Armadura (10 + Des)';
  document.getElementById('eqShieldCheck').checked = !!st.equipped_shield;
  document.getElementById('eqAcBonus').value = st.armor_magic_bonus || 0;

  const wCont = document.getElementById('weaponsEditorContainer');
  wCont.innerHTML = '';
  const weapons = st.weapons || [];
  for (let i = 0; i < 3; i++) {
    const w = weapons[i] || {name: '-- Seleccionar Arma --', ability: 'Fuerza', damage: '', mastery: 'Ninguna'};
    const wOpts = catalogs.weapons.map(wn => `<option value="${wn}" ${wn === w.name ? 'selected' : ''}>${wn}</option>`).join('');
    const calcInfo = (d.weapons && d.weapons[i]) ? d.weapons[i] : {atk: '+0', mastery_desc: ''};
    wCont.innerHTML += `
      <div style="background:var(--card-alt);padding:8px;border-radius:8px;margin-bottom:6px;border:1px solid var(--border);">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px;">
          <span style="font-size:0.78rem;color:var(--muted);font-weight:bold;">Ranura de Arma #${i+1}</span>
          <span class="badge" style="font-size:0.82rem;">${calcInfo.atk}</span>
        </div>
        <select id="w_name_${i}" onchange="onMobileWeaponPresetChange(${i})">${wOpts}</select>
        <div class="grid-2" style="margin-top:5px;">
          <select id="w_abil_${i}">
            <option value="Fuerza" ${w.ability === 'Fuerza' ? 'selected' : ''}>Fuerza</option>
            <option value="Destreza" ${w.ability === 'Destreza' ? 'selected' : ''}>Destreza</option>
          </select>
          <input id="w_dmg_${i}" value="${w.damage || ''}" placeholder="Daño (ej. 1d8)">
        </div>
        <div class="sub-note" style="color:var(--gold);margin-top:4px;">Maestría (${w.mastery || 'Ninguna'}): <span style="color:var(--muted);">${calcInfo.mastery_desc || ''}</span></div>
        <input type="hidden" id="w_mast_${i}" value="${w.mastery || 'Ninguna'}">
      </div>
    `;
  }

  const abGrid = document.getElementById('abilitiesGrid');
  abGrid.innerHTML = d.abilities.map(a => `
    <div class="stat-box">
      <div class="lbl">${a.name.slice(0,3)} (${a.score})</div>
      <div class="val">${a.mod}</div>
      <div class="sub-note">Salv: ${a.save}</div>
    </div>
  `).join('');

  populateShardTabFromCharacter();
  renderMobileSpellsTab();

  const cp = (d.coins && d.coins.cp) ? d.coins.cp : 0;
  const sp = (d.coins && d.coins.sp) ? d.coins.sp : 0;
  const gp = (d.coins && d.coins.gp) ? d.coins.gp : 0;
  document.getElementById('cpInput').value = cp;
  document.getElementById('spInput').value = sp;
  document.getElementById('gpInput').value = gp;
  document.getElementById('shopPlayerWallet').textContent = `${gp} PO | ${sp} PP | ${cp} PC`;

  // Ranuras de Sintonización
  const att = st.attuned_items || ['', '', ''];
  let activeAtt = 0;
  for (let i = 0; i < 3; i++) {
    const val = att[i] ? att[i] : '-- Ranura Libre --';
    const sel = document.getElementById(`attuneSlot${i}`);
    if (sel) sel.value = val;
    if (val !== '-- Ranura Libre --') activeAtt++;
  }
  document.getElementById('attuneCountBadge').textContent = `${activeAtt} / 3 sintonizados`;

  document.getElementById('mountTypeSelect').value = st.mount_type || 'Sin Montura';
  renderMobileInventories();

  document.getElementById('passivesBanner').textContent = d.passives_text;
  document.getElementById('skillsList').innerHTML = d.skills.map(s => `
    <div class="row-item"><span>${s.name}</span><span class="badge">${s.bonus}</span></div>
  `).join('');
  document.getElementById('featuresText').textContent = d.features_summary;
  document.getElementById('adventureNotesArea').value = st.adventure_notes || '';
}

async function saveAttunementMobile(changedIdx) {
  if (!currentCharId) return;
  const s0 = document.getElementById('attuneSlot0').value;
  const s1 = document.getElementById('attuneSlot1').value;
  const s2 = document.getElementById('attuneSlot2').value;
  const arr = [s0, s1, s2];
  const chosen = arr[changedIdx];

  if (chosen !== '-- Ranura Libre --' && arr.filter(x => x === chosen).length > 1) {
    alert(`Regla de Sintonización (Pág. 232): No puedes sintonizarte con más de una copia de '${chosen}' a la vez.`);
    document.getElementById(`attuneSlot${changedIdx}`).value = '-- Ranura Libre --';
    return;
  }

  const clean = arr.map(x => x === '-- Ranura Libre --' ? '' : x);
  await fetch('/api/update_status', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: currentCharId, attuned_items: clean})
  });
  await loadCharDetail();
}

// =========================================================================
// TIENDA Y TABERNA EN VIVO DEL DM (COMPRA Y VENTA AUTOMÁTICA)
// =========================================================================
async function loadMobileShop() {
  const res = await fetch('/api/shop');
  currentShopData = await res.json();
  renderShopCatalogMobile();
}

function renderShopCatalogMobile() {
  if (!currentShopData) return;
  document.getElementById('shopHeaderName').textContent = `🏪 ${currentShopData.shop_name}`;
  const multPct = Math.round((currentShopData.price_multiplier || 1.0) * 100);
  document.getElementById('shopPresetSubtitle').textContent =
    `${currentShopData.shop_preset} — Precios al ${multPct}%`;

  const box = document.getElementById('shopCatalogContainer');
  if (!currentShopData.is_open) {
    box.innerHTML = `<div style="text-align:center;padding:20px;color:var(--red);font-weight:bold;">🔒 El DM ha cerrado esta tienda por ahora.</div>`;
    return;
  }

  const q = (document.getElementById('shopSearchInput').value || '').trim().toLowerCase();
  let html = '';

  Object.keys(currentShopData.categories).forEach(catName => {
    const items = currentShopData.categories[catName].filter(it =>
      !q || it.name.toLowerCase().includes(q) || (it.desc || '').toLowerCase().includes(q)
    );
    if (!items.length) return;

    html += `<div style="background:#334155;padding:6px 10px;border-radius:6px;font-weight:bold;margin-top:8px;font-size:0.85rem;color:var(--gold);">${catName}</div>`;
    items.forEach(it => {
      const safeItem = encodeURIComponent(JSON.stringify(it));
      html += `
        <div class="row-item">
          <div style="flex:1;">
            <strong>${it.name}</strong> <span class="sub-note">(${it.weight_kg} kg)</span>
            ${it.desc ? `<div class="sub-note">${it.desc}</div>` : ''}
          </div>
          <div style="text-align:right;">
            <div style="color:var(--gold);font-weight:bold;font-size:0.85rem;margin-bottom:3px;">${it. adjusted_price_str}</div>
            <button class="btn-sm" style="background:var(--green);" onclick="buyShopItemMobile('${safeItem}')">Comprar</button>
          </div>
        </div>
      `;
    });
  });

  box.innerHTML = html || '<div class="sub-note">No se encontraron artículos con ese filtro.</div>';
}

async function buyShopItemMobile(encodedItem) {
  if (!currentCharId) { alert('Selecciona primero tu personaje arriba.'); return; }
  const item = JSON.parse(decodeURIComponent(encodedItem));
  const qty = Math.max(1, parseInt(document.getElementById('shopBuyQty').value || 1));
  const dest = document.getElementById('shopBuyDestSelect').value;

  const res = await fetch('/api/shop_buy', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: currentCharId, item: item, qty: qty, target: dest})
  });
  const out = await res.json();
  alert(out.msg || (out.ok ? 'Compra realizada' : 'Error en compra'));
  if (out.ok) {
    await loadCharDetail();
  }
}

async function sellInvItemMobile(targetKey, idx, subIdx = null) {
  if (!currentCharId) return;
  if (!confirm('💰 ¿Vender 1 unidad de este objeto a la mitad de su precio oficial de compra (Regla Pág. 213)?')) return;
  const res = await fetch('/api/shop_sell', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: currentCharId, target: targetKey, index: idx, sub_index: subIdx})
  });
  const out = await res.json();
  if (out.msg) alert(out.msg);
  await loadCharDetail();
}

function onMobileWeaponPresetChange(slotIdx) {
  const wName = document.getElementById(`w_name_${slotIdx}`).value;
  const tpl = catalogs.weapons_full[wName];
  if (!tpl) return;
  document.getElementById(`w_dmg_${slotIdx}`).value = tpl.damage || '';
  document.getElementById(`w_mast_${slotIdx}`).value = tpl.mastery || 'Ninguna';
  document.getElementById(`w_abil_${slotIdx}`).value = tpl.ability || 'Fuerza';
}

function startBlankCharacterInShard() {
  if (!catalogs) return;
  currentCharId = null;
  charData = {
    id: null, name: '', player_name: '', species: 'Humano', background: 'Acólito',
    char_class: 'Guerrero', subclass: 'Se elige en Nivel 3', level: 1,
    stats: {
      base_scores: {Fuerza:10, Destreza:10, Constitución:10, Inteligencia:10, Sabiduría:10, Carisma:10},
      bg_bonuses: {'+1_a':'Ninguno', '+1_b':'Ninguno', '+1_c':'Ninguno'},
      class_skill_choices: [], skilled_feat_choices: [], instrument_choices: [],
      language_choices: ['Común', 'Ninguno', 'Ninguno'], level_progression_choices: {},
      xp_current: 0
    }
  };
  document.getElementById('charSelect').value = '';
  populateShardTabFromCharacter();
  showTab('tabShard', document.getElementById('btnTabShard'));
}

function populateShardTabFromCharacter() {
  if (!charData || !catalogs) return;
  const st = charData.stats || {};
  document.getElementById('sh_name').value = charData.name || '';
  document.getElementById('sh_player').value = charData.player_name || '';
  document.getElementById('sh_species').value = charData.species || 'Humano';
  document.getElementById('sh_bg').value = charData.background || 'Acólito';
  document.getElementById('sh_class').value = charData.char_class || 'Guerrero';
  document.getElementById('sh_level').value = String(charData.level || 1);
  document.getElementById('sh_xp').value = st.xp_current || 0;

  const baseScores = st.base_scores || st.scores || {};
  catalogs.abilities.forEach(ab => {
    const inp = document.getElementById(`sh_base_${ab}`);
    if (inp) inp.value = baseScores[ab] !== undefined ? baseScores[ab] : 10;
  });

  rebuildShardProgressiveOptions();
}

function applyStdArrayInShard() {
  const cls = document.getElementById('sh_class').value;
  const std = catalogs.std_scores[cls];
  if (!std) return;
  Object.keys(std).forEach(ab => {
    const inp = document.getElementById(`sh_base_${ab}`);
    if (inp) inp.value = std[ab];
  });
  updateShardSuggestedHp();
}

function makeAlertSelectHtml(id, labelText, options, currentVal) {
  const val = options.includes(currentVal) ? currentVal : options[0];
  const isEmpty = (val === 'Ninguno' || val === 'Ninguna' || val === '');
  const iconCls = isEmpty ? 'status-warn' : 'status-ok';
  const iconTxt = isEmpty ? '!' : 'OK';
  const optsHtml = options.map(o => `<option value="${o}" ${o === val ? 'selected' : ''}>${o}</option>`).join('');
  return `
    <div class="alert-row">
      <div id="ico_${id}" class="status-icon ${iconCls}">${iconTxt}</div>
      <div style="flex:1;">
        <select id="${id}" onchange="updateAlertIcon('${id}')">${optsHtml}</select>
        <div class="sub-note">${labelText}</div>
      </div>
    </div>
  `;
}

function updateAlertIcon(id) {
  const el = document.getElementById(id);
  const ico = document.getElementById(`ico_${id}`);
  if (!el || !ico) return;
  const empty = (el.value === 'Ninguno' || el.value === 'Ninguna' || el.value === '');
  ico.className = 'status-icon ' + (empty ? 'status-warn' : 'status-ok');
  ico.textContent = empty ? '!' : 'OK';
  updateShardSuggestedHp();
}

function updateShardSuggestedHp() {
  if (!catalogs) return;
  const cls = document.getElementById('sh_class').value;
  const sp = document.getElementById('sh_species').value;
  const bg = document.getElementById('sh_bg').value;
  const lvl = parseInt(document.getElementById('sh_level').value || 1);
  const bgInfo = catalogs.backgrounds_full[bg] || {feat: ''};
  document.getElementById('sh_origin_feat').value = bgInfo.feat || '';

  let conScore = parseInt((document.getElementById('sh_base_Constitución') || {}).value || 10);
  ['sh_bg_b1','sh_bg_b2','sh_bg_b3'].forEach(id => {
    const el = document.getElementById(id);
    if (el && el.value === 'Constitución') conScore++;
  });
  const conMod = Math.floor((conScore - 10) / 2);
  const hd = (catalogs.classes_full[cls] || {}).hit_die || 8;
  const avg = Math.floor(hd / 2) + 1;
  let hp = hd + conMod + ((lvl - 1) * (avg + conMod));
  if ((bgInfo.feat || '').includes('Duro')) hp += 2 * lvl;
  if (sp === 'Enano') hp += lvl;
  document.getElementById('shardSuggestedHp').textContent = `${Math.max(1, hp)} PG Sugeridos`;
}

function rebuildShardProgressiveOptions() {
  if (!catalogs) return;
  const sp = document.getElementById('sh_species').value;
  const bg = document.getElementById('sh_bg').value;
  const cls = document.getElementById('sh_class').value;
  const lvl = parseInt(document.getElementById('sh_level').value || 1);

  document.getElementById('shardHeaderTitle').textContent = `Opciones Shard (${cls} Niv. 1 a ${lvl})`;

  const st = (charData && charData.stats) ? charData.stats : {};
  const savedProg = st.level_progression_choices || {};
  const bgInfo = catalogs.backgrounds_full[bg] || {abilities: catalogs.abilities, feat: '', skills: [], tool: ''};
  const clsInfo = catalogs.classes_full[cls] || {skill_choices_count: 2, skill_pool: catalogs.skills, instruments_count: 0, subclasses: []};
  const allSkills = ['Ninguna', ...catalogs.skills];

  let html = '';

  html += `<div class="card"><div style="font-weight:bold;color:#60a5fa;margin-bottom:4px;">NIVEL 1 — Especie (${sp}) y Trasfondo (${bg})</div>`;
  if (catalogs.lineages[sp]) {
    html += makeAlertSelectHtml('sh_prog_species_lineage', `Linaje / Ancestría de ${sp}`, ['Ninguno', ...catalogs.lineages[sp]], st.species_lineage || savedProg.species_lineage || 'Ninguno');
  }
  if (sp === 'Humano') {
    html += makeAlertSelectHtml('sh_prog_human_extra_skill', 'Rasgo Humano Habilidoso (+1 Habilidad)', allSkills, st.human_extra_skill || savedProg.human_extra_skill || 'Ninguna');
  }
  const savedLangs = st.language_choices || ['Común', 'Ninguno', 'Ninguno'];
  html += makeAlertSelectHtml('sh_lang_1', 'Idioma Estándar Adicional #1', ['Ninguno', ...catalogs.languages], savedLangs[1] || 'Ninguno');
  html += makeAlertSelectHtml('sh_lang_2', 'Idioma Estándar Adicional #2', ['Ninguno', ...catalogs.languages], savedLangs[2] || 'Ninguno');

  html += `<div class="sub-note" style="margin-top:8px;color:var(--gold);">Trasfondo ${bg}: Habilidades fijas (${bgInfo.skills.join(', ')}) | Dote: ${bgInfo.feat}</div>`;
  const bgAbilPool = ['Ninguno', ...catalogs.abilities];
  const savedBgB = st.bg_bonuses || {};
  html += makeAlertSelectHtml('sh_bg_b1', 'Aumento de Trasfondo +1 (#1)', bgAbilPool, savedBgB['+1_a'] || 'Ninguno');
  html += makeAlertSelectHtml('sh_bg_b2', 'Aumento de Trasfondo +1 (#2)', bgAbilPool, savedBgB['+1_b'] || 'Ninguno');
  html += makeAlertSelectHtml('sh_bg_b3', 'Aumento de Trasfondo +1 (#3)', bgAbilPool, savedBgB['+1_c'] || 'Ninguno');

  if ((bgInfo.feat || '').includes('Habilidoso') || sp === 'Humano') {
    const skSaved = st.skilled_feat_choices || [];
    for (let i = 0; i < 3; i++) {
      html += makeAlertSelectHtml(`sh_skilled_${i}`, `Dote Habilidoso (Skilled) — Habilidad #${i+1}`, allSkills, skSaved[i] || 'Ninguna');
    }
  }
  html += `</div>`;

  html += `<div class="card"><div style="font-weight:bold;color:var(--green);margin-bottom:4px;">NIVEL 1 — Opciones Iniciales de ${cls}</div>`;
  const clsSkillPool = ['Ninguna', ...(clsInfo.skill_pool || catalogs.skills)];
  const savedClsSk = st.class_skill_choices || [];
  for (let i = 0; i < (clsInfo.skill_choices_count || 2); i++) {
    html += makeAlertSelectHtml(`sh_cls_sk_${i}`, `Habilidad de ${cls} #${i+1}`, clsSkillPool, savedClsSk[i] || 'Ninguna');
  }
  const savedInst = st.instrument_choices || [];
  for (let i = 0; i < (clsInfo.instruments_count || 0); i++) {
    html += makeAlertSelectHtml(`sh_inst_${i}`, `Instrumento Musical #${i+1}`, ['Ninguno', ...catalogs.instruments], savedInst[i] || 'Ninguno');
  }

  if (cls === 'Clérigo') {
    html += makeAlertSelectHtml('sh_prog_lvl1_order', 'Orden Divina (Clérigo Nivel 1)', ['Ninguna', 'Protector (Armaduras pesadas y armas marciales)', 'Taumaturgo (+1 Truco y +Sab a Religión/Arcano)'], savedProg.lvl1_order || 'Ninguna');
  } else if (cls === 'Druida') {
    html += makeAlertSelectHtml('sh_prog_lvl1_order', 'Orden Primigenia (Druida Nivel 1)', ['Ninguna', 'Guardián (Armaduras medias y armas marciales)', 'Naturalista (+1 Truco y +Sab a Naturaleza/Arcano)'], savedProg.lvl1_order || 'Ninguna');
  } else if (cls === 'Guerrero') {
    html += makeAlertSelectHtml('sh_prog_lvl1_style', 'Estilo de Combate (Guerrero Nivel 1)', ['Ninguno', ...catalogs.fighting_styles], savedProg.lvl1_style || 'Ninguno');
  } else if (cls === 'Pícaro') {
    html += makeAlertSelectHtml('sh_prog_lvl1_exp_1', 'Pericia de Pícaro Nivel 1 (★★ #1)', allSkills, savedProg.lvl1_exp_1 || 'Ninguna');
    html += makeAlertSelectHtml('sh_prog_lvl1_exp_2', 'Pericia de Pícaro Nivel 1 (★★ #2)', allSkills, savedProg.lvl1_exp_2 || 'Ninguna');
  } else if (cls === 'Brujo') {
    html += makeAlertSelectHtml('sh_prog_lvl1_invoc_1', 'Invocación Sobrenatural #1 (Nivel 1)', ['Ninguna', ...catalogs.invocations], savedProg.lvl1_invoc_1 || 'Ninguna');
  }
  html += `</div>`;

  const asiLevels = (cls === 'Guerrero') ? [4,6,8,12,14,16] : ((cls === 'Pícaro') ? [4,8,10,12,16] : [4,8,12,16]);

  for (let l = 2; l <= lvl; l++) {
    let lvlInner = '';
    if (l === 2) {
      if (cls === 'Bardo') {
        lvlInner += `<div class="sub-note" style="color:var(--green);">✔ Aprendiz de mucho activado (+mitad de competencia).</div>`;
        lvlInner += makeAlertSelectHtml('sh_prog_lvl2_exp_1', 'Pericia de Bardo Nivel 2 (★★ #1)', allSkills, savedProg.lvl2_exp_1 || 'Ninguna');
        lvlInner += makeAlertSelectHtml('sh_prog_lvl2_exp_2', 'Pericia de Bardo Nivel 2 (★★ #2)', allSkills, savedProg.lvl2_exp_2 || 'Ninguna');
      } else if (cls === 'Explorador' || cls === 'Paladín') {
        lvlInner += makeAlertSelectHtml('sh_prog_lvl2_style', `Estilo de Combate (${cls} Nivel 2)`, ['Ninguno', ...catalogs.fighting_styles], savedProg.lvl2_style || 'Ninguno');
        if (cls === 'Explorador') {
          lvlInner += makeAlertSelectHtml('sh_prog_lvl2_exp_1', 'Explorador Hábil: Pericia en 1 Habilidad (★★)', allSkills, savedProg.lvl2_exp_1 || 'Ninguna');
        }
      } else if (cls === 'Mago') {
        lvlInner += makeAlertSelectHtml('sh_prog_lvl2_exp_1', 'Erudito (Mago Nivel 2): Pericia Académica (★★)', ['Ninguna', 'Conocimiento Arcano', 'Historia', 'Investigación', 'Medicina', 'Naturaleza', 'Religión'], savedProg.lvl2_exp_1 || 'Ninguna');
      } else if (cls === 'Brujo') {
        lvlInner += makeAlertSelectHtml('sh_prog_lvl2_invoc_2', 'Invocación Sobrenatural #2 (Nivel 2)', ['Ninguna', ...catalogs.invocations], savedProg.lvl2_invoc_2 || 'Ninguna');
        lvlInner += makeAlertSelectHtml('sh_prog_lvl2_invoc_3', 'Invocación Sobrenatural #3 (Nivel 2)', ['Ninguna', ...catalogs.invocations], savedProg.lvl2_invoc_3 || 'Ninguna');
      }
    }

    if (l === 3) {
      const subPool = ['Ninguna', ...(clsInfo.subclasses || [])];
      const currSub = (charData && charData.subclass && charData.subclass !== 'Se elige en Nivel 3') ? charData.subclass : (savedProg.lvl3_subclass || 'Ninguna');
      lvlInner += makeAlertSelectHtml('sh_prog_lvl3_subclass', `Subclase de ${cls} (Nivel 3)`, subPool, currSub);
      if (cls === 'Bardo') {
        lvlInner += makeAlertSelectHtml('sh_prog_lvl3_lore_sk_1', 'Si elegiste Colegio del Conocimiento: Habilidad #1', allSkills, savedProg.lvl3_lore_sk_1 || 'Ninguna');
        lvlInner += makeAlertSelectHtml('sh_prog_lvl3_lore_sk_2', 'Si elegiste Colegio del Conocimiento: Habilidad #2', allSkills, savedProg.lvl3_lore_sk_2 || 'Ninguna');
        lvlInner += makeAlertSelectHtml('sh_prog_lvl3_lore_sk_3', 'Si elegiste Colegio del Conocimiento: Habilidad #3', allSkills, savedProg.lvl3_lore_sk_3 || 'Ninguna');
      } else if (cls === 'Bárbaro') {
        lvlInner += makeAlertSelectHtml('sh_prog_lvl3_primal_sk', 'Conocimiento Primigenio: +1 Habilidad de Bárbaro', clsSkillPool, savedProg.lvl3_primal_sk || 'Ninguna');
      }
    }

    if (asiLevels.includes(l)) {
      lvlInner += makeAlertSelectHtml(`sh_prog_lvl${l}_feat`, `Dote General o Mejora (Nivel ${l})`, ['Ninguna', ...catalogs.general_feats], savedProg[`lvl${l}_feat`] || 'Mejora de característica (+2 a una o +1 a dos)');
      lvlInner += makeAlertSelectHtml(`sh_prog_lvl${l}_ab1`, `Aumento +1 Característica A (Nivel ${l})`, ['Ninguno', ...catalogs.abilities], savedProg[`lvl${l}_ab1`] || 'Ninguno');
      lvlInner += makeAlertSelectHtml(`sh_prog_lvl${l}_ab2`, `Aumento +1 Característica B (Nivel ${l})`, ['Ninguno', ...catalogs.abilities], savedProg[`lvl${l}_ab2`] || 'Ninguno');
    }

    if (l === 5 && cls === 'Brujo') {
      lvlInner += makeAlertSelectHtml('sh_prog_lvl5_invoc_4', 'Invocación Sobrenatural #4 (Nivel 5)', ['Ninguna', ...catalogs.invocations], savedProg.lvl5_invoc_4 || 'Ninguna');
      lvlInner += makeAlertSelectHtml('sh_prog_lvl5_invoc_5', 'Invocación Sobrenatural #5 (Nivel 5)', ['Ninguna', ...catalogs.invocations], savedProg.lvl5_invoc_5 || 'Ninguna');
    }

    if (l === 6 && cls === 'Pícaro') {
      lvlInner += makeAlertSelectHtml('sh_prog_lvl6_exp_1', 'Pericia Adicional Pícaro Nivel 6 (★★ #1)', allSkills, savedProg.lvl6_exp_1 || 'Ninguna');
      lvlInner += makeAlertSelectHtml('sh_prog_lvl6_exp_2', 'Pericia Adicional Pícaro Nivel 6 (★★ #2)', allSkills, savedProg.lvl6_exp_2 || 'Ninguna');
    }

    if (l === 7 && cls === 'Clérigo') {
      lvlInner += makeAlertSelectHtml('sh_prog_lvl7_blessed', 'Golpes Benditos (Clérigo Nivel 7)', ['Ninguno', 'Golpe divino (+1d8 radiante/necrótico con armas)', 'Lanzamiento potente (+Sab al daño de trucos)'], savedProg.lvl7_blessed || 'Ninguno');
    }

    if (l === 7 && cls === 'Druida') {
      lvlInner += makeAlertSelectHtml('sh_prog_lvl7_elem_fury', 'Furia Elemental (Druida Nivel 7)', ['Ninguna', 'Golpe primordial (+1d8 elemental en ataques)', 'Lanzamiento potente (+Sab al daño de trucos)'], savedProg.lvl7_elem_fury || 'Ninguna');
    }

    if (l === 9 && (cls === 'Bardo' || cls === 'Explorador')) {
      lvlInner += makeAlertSelectHtml('sh_prog_lvl9_exp_1', `Pericia Adicional ${cls} Nivel 9 (★★ #1)`, allSkills, savedProg.lvl9_exp_1 || 'Ninguna');
      lvlInner += makeAlertSelectHtml('sh_prog_lvl9_exp_2', `Pericia Adicional ${cls} Nivel 9 (★★ #2)`, allSkills, savedProg.lvl9_exp_2 || 'Ninguna');
    }

    if (l === 19) {
      lvlInner += makeAlertSelectHtml('sh_prog_lvl19_boon', 'Don Épico (Nivel 19)', ['Ninguno', ...catalogs.epic_boons], savedProg.lvl19_boon || 'Ninguno');
    }

    const featsAtLvl = (clsInfo.features_by_level || {})[l] || [];
    const featTitle = featsAtLvl.map(f => f[0]).join(', ') || 'Progresión de Nivel';

    html += `
      <div class="card">
        <div style="font-weight:bold;color:var(--gold);margin-bottom:4px;">NIVEL ${l} — ${featTitle}</div>
        ${lvlInner || '<div class="sub-note">Rasgos automáticos y progresión de espacios de conjuro desbloqueados en este nivel.</div>'}
      </div>
    `;
  }

  document.getElementById('shardDynamicLevelsContainer').innerHTML = html;
  updateShardSuggestedHp();
}

async function saveShardProgressionFromMobile() {
  try {
    const name = document.getElementById('sh_name').value.trim();
    if (!name) { alert('Escribe el nombre de tu personaje arriba.'); return; }

    const baseScores = {};
    catalogs.abilities.forEach(ab => {
      baseScores[ab] = parseInt(document.getElementById(`sh_base_${ab}`).value || 10);
    });

    const progChoices = {};
    document.querySelectorAll('[id^="sh_prog_"]').forEach(el => {
      const key = el.id.replace('sh_prog_', '');
      progChoices[key] = el.value;
    });

    const clsSkills = [];
    document.querySelectorAll('[id^="sh_cls_sk_"]').forEach(el => {
      if (el.value && el.value !== 'Ninguna') clsSkills.push(el.value);
    });

    const skilledSkills = [];
    document.querySelectorAll('[id^="sh_skilled_"]').forEach(el => {
      if (el.value && el.value !== 'Ninguna') skilledSkills.push(el.value);
    });

    const insts = [];
    document.querySelectorAll('[id^="sh_inst_"]').forEach(el => {
      if (el.value && el.value !== 'Ninguno') insts.push(el.value);
    });

    const langs = ['Común'];
    ['sh_lang_1', 'sh_lang_2'].forEach(id => {
      const el = document.getElementById(id);
      if (el && el.value && el.value !== 'Ninguno') langs.push(el.value);
    });

    const payload = {
      id: currentCharId,
      name: name,
      player_name: document.getElementById('sh_player').value.trim() || 'Jugador',
      species: document.getElementById('sh_species').value,
      background: document.getElementById('sh_bg').value,
      char_class: document.getElementById('sh_class').value,
      level: parseInt(document.getElementById('sh_level').value || 1),
      xp_current: parseInt(document.getElementById('sh_xp').value || 0),
      base_scores: baseScores,
      bg_bonuses: {
        '+1_a': document.getElementById('sh_bg_b1').value,
        '+1_b': document.getElementById('sh_bg_b2').value,
        '+1_c': document.getElementById('sh_bg_b3').value
      },
      class_skill_choices: clsSkills,
      skilled_feat_choices: skilledSkills,
      instrument_choices: insts,
      language_choices: langs,
      level_progression_choices: progChoices
    };

    const res = await fetch('/api/save_shard_character', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload)
    });
    const out = await res.json();
    if (out.ok) {
      alert('¡Personaje guardado y sincronizado con la PC del DM!');
      await fetchCharacters(out.id);
      showTab('tabSheet', document.getElementById('btnTabSheet'));
    } else {
      alert('Error al guardar: ' + (out.error || 'Desconocido'));
    }
  } catch (err) {
    alert('Error de conexión al guardar personaje: ' + err);
  }
}

async function saveCombatAndEquipment() {
  if (!currentCharId) return;
  const weapons = [];
  for (let i = 0; i < 3; i++) {
    weapons.push({
      name: document.getElementById(`w_name_${i}`).value,
      ability: document.getElementById(`w_abil_${i}`).value,
      damage: document.getElementById(`w_dmg_${i}`).value,
      mastery: document.getElementById(`w_mast_${i}`).value
    });
  }
  const payload = {
    id: currentCharId,
    hp_current: document.getElementById('hpCurrInput').value,
    hp_max: document.getElementById('hpMaxInput').value,
    hp_temp: document.getElementById('hpTempInput').value,
    heroic_inspiration: document.getElementById('inspCheck').checked,
    equipped_armor: document.getElementById('eqArmorSelect').value,
    equipped_shield: document.getElementById('eqShieldCheck').checked,
    armor_magic_bonus: parseInt(document.getElementById('eqAcBonus').value || 0),
    weapons: weapons,
    coins: {
      cp: parseInt(document.getElementById('cpInput').value || 0),
      sp: parseInt(document.getElementById('spInput').value || 0),
      gp: parseInt(document.getElementById('gpInput').value || 0)
    }
  };
  await fetch('/api/update_status', {
    method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload)
  });
  await loadCharDetail();
}

async function openShortRestPrompt() {
  if (!charData) return;
  const spent = parseInt(prompt(`⛺ DESCANSO CORTO\nTienes ${charData.hit_dice} Dados de Golpe (d${charData.hit_die_faces}).\n¿Cuántos Dados de Golpe vas a gastar?`, "1") || "0");
  if (spent <= 0) return;
  const rollSum = parseInt(prompt(`Tira ${spent}d${charData.hit_die_faces} físicos en la mesa.\n¿Cuánto sumaron tus dados físicos (sin sumar Constitución)?`, "5") || "0");
  const res = await fetch('/api/rest_or_levelup', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: currentCharId, action: 'short_rest', dice_spent: spent, roll_sum: rollSum})
  });
  const out = await res.json();
  if (out.msg) alert(out.msg);
  await loadCharDetail();
}

async function takeLongRestMobile() {
  if (!charData) return;
  if (!confirm('🌙 ¿Realizar un Descanso Largo (Reglas 5.5e)?\nRestaurará todos tus PG, Dados de Golpe y Espacios de Conjuro.')) return;
  const res = await fetch('/api/rest_or_levelup', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: currentCharId, action: 'long_rest'})
  });
  const out = await res.json();
  if (out.msg) alert(out.msg);
  await loadCharDetail();
}

async function openLevelUpPrompt() {
  if (!charData) return;
  const avg = Math.floor(charData.hit_die_faces / 2) + 1;
  const dieVal = parseInt(prompt(`⬆️ SUBIR A NIVEL ${charData.level + 1}\nTira 1d${charData.hit_die_faces} físico en la mesa (o deja el promedio fijo de ${avg}):`, String(avg)) || String(avg));
  const res = await fetch('/api/rest_or_levelup', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: currentCharId, action: 'level_up', die_val: dieVal})
  });
  const out = await res.json();
  if (out.msg) alert(out.msg);
  await loadCharDetail();
  showTab('tabShard', document.getElementById('btnTabShard'));
}

function renderMobileSpellsTab() {
  if (!charData || !catalogs) return;
  const d = charData;
  document.getElementById('spellStatsBanner').textContent = `Aptitud: ${d.spell_ability} | CD Salvación: ${d.spell_dc} | Ataque Mágico: +${d.spell_atk}`;

  const slotsBox = document.getElementById('spellSlotsTracker');
  const slots = d.slots_dict || {};
  const spent = (d.stats && d.stats.spent_spell_slots) ? d.stats.spent_spell_slots : {};
  if (Object.keys(slots).length === 0) {
    slotsBox.innerHTML = `<div class="sub-note">Tu clase/nivel actual no dispone de espacios de conjuro.</div>`;
  } else {
    let sHtml = '';
    Object.keys(slots).forEach(lvl => {
      const total = slots[lvl];
      const used = parseInt(spent[lvl] || 0);
      let checks = '';
      for (let i = 0; i < total; i++) {
        const isSpent = i < used;
        checks += `<input type="checkbox" ${isSpent ? 'checked' : ''} onchange="toggleSpellSlotMobile('${lvl}', ${i}, this.checked)" style="width:18px;height:18px;">`;
      }
      sHtml += `<div class="slot-pill"><strong>Niv. ${lvl}:</strong> ${checks} <span class="sub-note">(${total - used}/${total} disp.)</span></div>`;
    });
    slotsBox.innerHTML = sHtml;
  }

  const alwaysBox = document.getElementById('alwaysPreparedBox');
  alwaysBox.textContent = (d.always_prepared && d.always_prepared.length)
    ? `✔ Siempre Preparados (Gratis por Clase/Subclase): ${d.always_prepared.join(', ')}`
    : '';

  renderMobileSpellPicker();
}

async function toggleSpellSlotMobile(slotLvl, idx, isChecked) {
  if (!charData) return;
  const spent = (charData.stats.spent_spell_slots) || {};
  let curr = parseInt(spent[slotLvl] || 0);
  curr = isChecked ? curr + 1 : Math.max(0, curr - 1);
  spent[slotLvl] = curr;
  charData.stats.spent_spell_slots = spent;
  await fetch('/api/update_spells', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: currentCharId, spent_spell_slots: spent})
  });
  renderMobileSpellsTab();
}

function renderMobileSpellPicker() {
  if (!charData || !catalogs) return;
  const d = charData;
  const st = d.stats;
  const selCantrips = new Set(st.selected_cantrips || []);
  const selSpells = new Set(st.selected_spells || []);

  document.getElementById('spellCountersLabel').textContent =
    `Trucos: ${selCantrips.size}/${d.max_cantrips} | Preparados (Niv 1-${d.max_spell_lvl}): ${selSpells.size}/${d.max_prepared}`;

  const q = (document.getElementById('spellSearchInput').value || '').trim().toLowerCase();
  const onlyCls = document.getElementById('chkOnlyMyClassSpells').checked;
  const maxLvl = Math.max(1, d.max_spell_lvl);
  const secretos = (d.char_class === 'Bardo' && d.level >= 10);

  let html = '';
  for (let lvl = 0; lvl <= maxLvl; lvl++) {
    const matching = catalogs.spells.filter(sp => {
      if (sp.level !== lvl) return false;
      if (onlyCls) {
        const allowed = new Set([d.char_class]);
        if (secretos) ['Clérigo', 'Druida', 'Mago'].forEach(c => allowed.add(c));
        if (!sp.classes.some(c => allowed.has(c))) return false;
      }
      if (q && !sp.name.toLowerCase().includes(q) && !sp.school.toLowerCase().includes(q)) return false;
      return true;
    });
    if (!matching.length) continue;

    html += `<div style="background:#334155;padding:6px 10px;border-radius:6px;font-weight:bold;margin-top:8px;font-size:0.85rem;">
      ${lvl === 0 ? `Trucos / Cantrips (${matching.length})` : `Conjuros de Nivel ${lvl} (${matching.length})`}
    </div>`;

    matching.forEach(sp => {
      const checked = (lvl === 0) ? selCantrips.has(sp.name) : selSpells.has(sp.name);
      const encName = encodeURIComponent(sp.name);
      html += `
        <div class="row-item">
          <label style="margin:0;display:flex;align-items:center;gap:8px;color:var(--text);flex:1;font-weight:normal;">
            <input type="checkbox" ${checked ? 'checked' : ''} onchange="onToggleSpellCheck('${encName}', ${lvl}, this)" style="width:18px;height:18px;">
            <span><strong>${sp.name}</strong> <span class="sub-note">(${sp.school})</span></span>
          </label>
          <button class="btn-sm" onclick="lookupSpellPdfMobile('${encName}')" style="background:#2B4C7E;">📖 PDF</button>
        </div>
      `;
    });
  }
  document.getElementById('spellPickerList').innerHTML = html || '<div class="sub-note">Sin conjuros que coincidan.</div>';
}

function onToggleSpellCheck(encodedName, lvl, chkEl) {
  const spellName = decodeURIComponent(encodedName);
  const st = charData.stats;
  const cSet = new Set(st.selected_cantrips || []);
  const sSet = new Set(st.selected_spells || []);

  if (lvl === 0) {
    if (chkEl.checked) {
      if (cSet.size >= charData.max_cantrips) {
        chkEl.checked = false;
        alert(`Máximo ${charData.max_cantrips} trucos permitidos en tu nivel.`);
        return;
      }
      cSet.add(spellName);
    } else cSet.delete(spellName);
    st.selected_cantrips = Array.from(cSet);
  } else {
    if (chkEl.checked) {
      if (sSet.size >= charData.max_prepared) {
        chkEl.checked = false;
        alert(`Máximo ${charData.max_prepared} conjuros preparados permitidos en tu nivel.`);
        return;
      }
      sSet.add(spellName);
    } else sSet.delete(spellName);
    st.selected_spells = Array.from(sSet);
  }
  renderMobileSpellPicker();
}

async function saveSelectedSpellsMobile() {
  if (!currentCharId || !charData) return;
  await fetch('/api/update_spells', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      id: currentCharId,
      selected_cantrips: charData.stats.selected_cantrips || [],
      selected_spells: charData.stats.selected_spells || []
    })
  });
  alert('¡Conjuros guardados y sincronizados con la PC!');
  await loadCharDetail();
}

async function lookupSpellPdfMobile(encodedName) {
  const spellName = decodeURIComponent(encodedName);
  const clean = spellName.split('(')[0].trim();
  const res = await fetch(`/api/search_pdf?q=${encodeURIComponent(clean)}`);
  const hits = await res.json();
  const card = document.getElementById('spellPdfPreviewCard');
  const box = document.getElementById('spellPdfPreviewText');
  card.style.display = 'block';
  if (!hits.length) {
    box.innerHTML = `No se encontró '${clean}' en los PDFs indexados.`;
    return;
  }
  box.innerHTML = hits.slice(0, 3).map(h => `
    <div style="margin-bottom:6px;">
      <strong style="color:var(--gold);">[${h.manual_title} — Pág. ${h.page_number}]:</strong> ${h.match_snippet}
    </div>
  `).join('');
}

function updateCatalogDestinations() {
  if (!charData) return;
  const st = charData.stats || {};
  const opts = [
    {label: '🎒 Inventario del Personaje', val: 'char:none'},
    {label: '🫏 Inventario de la Montura', val: 'mount:none'}
  ];
  (st.inventory_char || []).forEach((it, idx) => {
    if (it.is_container) opts.push({label: `↳ [Contenedor PJ] ${it.name}`, val: `char:${idx}`});
  });
  (st.inventory_mount || []).forEach((it, idx) => {
    if (it.is_container) opts.push({label: `↳ [Contenedor Montura] ${it.name}`, val: `mount:${idx}`});
  });
  const sel = document.getElementById('catDestSelect');
  const prev = sel.value;
  sel.innerHTML = opts.map(o => `<option value="${o.val}">${o.label}</option>`).join('');
  if (prev && opts.some(o => o.val === prev)) sel.value = prev;
}

function renderMobileItemCatalog() {
  if (!catalogs) return;
  const cat = document.getElementById('catCategorySelect').value;
  const q = (document.getElementById('catSearchInput').value || '').trim().toLowerCase();
  const box = document.getElementById('catItemsScroll');

  let html = '';
  Object.keys(catalogs.items_by_cat).forEach(catName => {
    if (cat !== 'Todas las Categorías' && cat !== catName) return;
    const matches = catalogs.items_by_cat[catName].filter(it =>
      !q || it.name.toLowerCase().includes(q) || (it.desc || '').toLowerCase().includes(q)
    );
    if (!matches.length) return;

    html += `<div style="color:var(--gold);font-weight:bold;font-size:0.8rem;margin:6px 0 3px 0;">${catName}</div>`;
    matches.forEach(it => {
      const safeJson = encodeURIComponent(JSON.stringify(it));
      const tag = it.is_container ? ' [Contenedor]' : (it.is_pack ? ' [Paquete]' : '');
      html += `
        <div class="row-item">
          <div style="flex:1;">
            <strong>${it.name}${tag}</strong> <span class="sub-note">(${it.weight_kg} kg | ${it.price || ''})</span>
            ${it.desc ? `<div class="sub-note">${it.desc}</div>` : ''}
          </div>
          <button class="btn-sm" onclick="addCatalogItemMobile('${safeJson}')">+ Añadir</button>
        </div>
      `;
    });
  });
  box.innerHTML = html || '<div class="sub-note">Sin objetos que coincidan.</div>';
}

async function addCatalogItemMobile(encodedTpl) {
  if (!currentCharId) return;
  const tpl = JSON.parse(decodeURIComponent(encodedTpl));
  const qty = Math.max(1, parseInt(document.getElementById('catQtyInput').value || 1));
  const dest = (document.getElementById('catDestSelect').value || 'char:none').split(':');

  await fetch('/api/inventory_op', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      id: currentCharId, op: 'add_catalog',
      target: dest[0], container_idx: dest[1] === 'none' ? null : parseInt(dest[1]),
      item_tpl: tpl, qty: qty
    })
  });
  await loadCharDetail();
}

async function addCustomItemMobile(target) {
  if (!currentCharId) return;
  const name = document.getElementById('custItemName').value.trim();
  if (!name) return;
  const qty = Math.max(1, parseInt(document.getElementById('custItemQty').value || 1));
  const kg = Math.max(0, parseFloat(document.getElementById('custItemKg').value || 0));
  const isCont = document.getElementById('custItemIsCont').checked;

  await fetch('/api/inventory_op', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      id: currentCharId, op: 'add_custom', target: target,
      name: name, qty: qty, weight_kg: kg, is_container: isCont
    })
  });
  document.getElementById('custItemName').value = '';
  document.getElementById('custItemIsCont').checked = false;
  await loadCharDetail();
}

async function invOpMobile(op, target, idx, subIdx = null) {
  await fetch('/api/inventory_op', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: currentCharId, op: op, target: target, index: idx, sub_index: subIdx})
  });
  await loadCharDetail();
}

async function changeMountTypeMobile() {
  if (!currentCharId) return;
  const mType = document.getElementById('mountTypeSelect').value;
  await fetch('/api/inventory_op', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: currentCharId, op: 'set_mount', mount_type: mType})
  });
  await loadCharDetail();
}

function renderInvListHtml(items, targetKey) {
  if (!items || !items.length) return '<div class="sub-note">Sin objetos registrados.</div>';
  let html = '';
  items.forEach((it, idx) => {
    const isCont = !!it.is_container;
    const exp = it.expanded !== false;
    const contents = it.contents || [];
    const transferBtn = targetKey === 'char'
      ? `<button class="btn-sm" style="background:#334155;" onclick="invOpMobile('transfer','char',${idx})">→🫏</button>`
      : `<button class="btn-sm" style="background:#334155;" onclick="invOpMobile('transfer','mount',${idx})">←🎒</button>`;

    if (isCont) {
      html += `
        <div class="cont-header" onclick="invOpMobile('toggle_expand','${targetKey}',${idx})">
          <span>${exp ? '▼' : '▶'} 📦 ${it.name} (${contents.length} ítems) — ${it.total_kg} kg</span>
          <div style="display:flex;gap:4px;" onclick="event.stopPropagation();">
            ${transferBtn}
            <button class="btn-sm" style="background:var(--red);" onclick="invOpMobile('remove','${targetKey}',${idx})">✕</button>
          </div>
        </div>
      `;
      if (exp) {
        html += `<div class="cont-body">`;
        if (!contents.length) {
          html += `<div class="sub-note">Contenedor vacío (elígelo en "Enviar a" arriba para meter objetos).</div>`;
        } else {
          contents.forEach((sub, sIdx) => {
            const subKg = Math.round(sub.qty * sub.weight_kg * 100) / 100;
            html += `
              <div class="row-item" style="padding:4px 0;">
                <span>↳ ${sub.name} (x${sub.qty}) — ${subKg} kg</span>
                <div style="display:flex;gap:4px;">
                  <button class="btn-sm" style="background:var(--orange);padding:3px 7px;" onclick="sellInvItemMobile('${targetKey}',${idx},${sIdx})">💰 50%</button>
                  <button class="btn-sm" style="background:#7f1d1d;padding:3px 7px;" onclick="invOpMobile('remove','${targetKey}',${idx},${sIdx})">✕</button>
                </div>
              </div>
            `;
          });
        }
        html += `</div>`;
      }
    } else {
      html += `
        <div class="row-item">
          <span>• ${it.name} (x${it.qty}) — ${it.total_kg} kg</span>
          <div style="display:flex;gap:4px;">
            <button class="btn-sm" style="background:var(--orange);" onclick="sellInvItemMobile('${targetKey}',${idx})">💰 50%</button>
            ${transferBtn}
            <button class="btn-sm" style="background:var(--red);" onclick="invOpMobile('remove','${targetKey}',${idx})">✕</button>
          </div>
        </div>
      `;
    }
  });
  return html;
}

function renderMobileInventories() {
  if (!charData) return;
  const d = charData;
  updateCatalogDestinations();

  const overChar = d.char_total_kg > d.char_max_kg;
  const cBadge = document.getElementById('charWeightBadge');
  cBadge.textContent = `${d.char_total_kg.toFixed(1)} / ${d.char_max_kg.toFixed(1)} kg` + (overChar ? ' ⚠️ SOBRECARGA' : '');
  cBadge.style.color = overChar ? 'var(--red)' : 'var(--green)';
  document.getElementById('charInvContainer').innerHTML = renderInvListHtml(d.char_inv_tree, 'char');

  const overMount = d.mount_max_kg > 0 && d.mount_total_kg > d.mount_max_kg;
  const mBadge = document.getElementById('mountWeightBadge');
  mBadge.textContent = `${d.mount_total_kg.toFixed(1)} / ${d.mount_max_kg.toFixed(1)} kg` + (overMount ? ' ⚠️ EXCESO' : '');
  mBadge.style.color = overMount ? 'var(--red)' : '#60a5fa';
  document.getElementById('mountInvContainer').innerHTML = renderInvListHtml(d.mount_inv_tree, 'mount');
}

async function saveAdventureNotesMobile() {
  if (!currentCharId) return;
  const notes = document.getElementById('adventureNotesArea').value;
  await fetch('/api/update_status', {
    method: 'POST', headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({id: currentCharId, adventure_notes: notes})
  });
  alert('¡Notas de aventura guardadas en la PC del DM!');
}

async function searchPdf() {
  const q = document.getElementById('pdfQuery').value;
  if (!q) return;
  const res = await fetch(`/api/search_pdf?q=${encodeURIComponent(q)}`);
  const hits = await res.json();
  const box = document.getElementById('pdfResults');
  if (!hits.length) { box.innerHTML = 'Sin resultados en los PDFs.'; return; }
  box.innerHTML = hits.map(h => `
    <div style="padding:8px 0;border-bottom:1px solid var(--border);">
      <div style="color:var(--gold);font-weight:bold;">${h.manual_title} — Pág. ${h.page_number}</div>
      <div class="sub-note" style="color:var(--text);">${h.match_snippet}</div>
    </div>
  `).join('');
}

initCatalogs().then(() => fetchCharacters());
async function loadLiveTableMobile() {
  const res = await fetch('/api/live_table');
  const st = await res.json();

  document.getElementById('liveEnvBanner').innerHTML = `
    <div><strong>Iluminación:</strong> <span style="color:var(--gold);">${st.lighting}</span></div>
    <div style="margin-top:4px;"><strong>Ritmo del Grupo:</strong> <span style="color:#60a5fa;">${st.travel_pace}</span></div>
  `;

  // Renderizar Iniciativa con Niebla de Guerra
  const cBox = document.getElementById('liveCombatList');
  const cHdr = document.getElementById('liveCombatHeader');
  if (!st.combat || !st.combat.active || !st.combat.combatants.length) {
    cHdr.textContent = '⚔️ Rastreador de Iniciativa (Sin combate activo)';
    cBox.innerHTML = '<div class="sub-note">El DM aún no ha iniciado un encuentro de combate.</div>';
  } else {
    cHdr.textContent = `⚔️ Combate en Curso — Asalto ${st.combat.round}`;
    cBox.innerHTML = st.combat.combatants.map(c => {
      const turnBg = c.is_turn ? 'background:#1e3a8a;border:1px solid #60a5fa;border-radius:8px;padding:8px;' : '';
      const badgeCol = c.status_tag === 'dead' ? 'var(--red)' : (c.status_tag === 'bloodied' ? 'var(--gold)' : 'var(--green)');
      const condTag = (c.condition && c.condition !== 'Sin Estado') ? ` <span style="color:var(--red);font-size:0.76rem;">[${c.condition}]</span>` : '';
      return `
        <div class="row-item" style="${turnBg}">
          <div>
            <strong>${c.is_turn ? '▶ ' : ''}${c.is_player ? '🛡️' : '🐉'} ${c.name}</strong>
            <span class="sub-note">(Inic. ${c.initiative})</span>${condTag}
          </div>
          <span style="font-weight:bold;font-size:0.82rem;color:${badgeCol};">${c.status_text}</span>
        </div>
      `;
    }).join('');
  }

  // Renderizar Mapa o Handout proyectado
  document.getElementById('liveHandoutTitle').textContent = `🖼️ ${st.handout_title || 'Sin imagen proyectada'}`;
  document.getElementById('liveHandoutCaption').textContent = st.handout_caption || '';
  const imgBox = document.getElementById('liveHandoutImgBox');
  if (st.handout_b64) {
    imgBox.innerHTML = `<img src="data:image/jpeg;base64,${st.handout_b64}" style="max-width:100%;border-radius:8px;border:1px solid var(--border);">`;
  } else {
    imgBox.innerHTML = '<div class="sub-note">Cuando el DM proyecte un mapa, carta o ilustración del manual, aparecerá aquí.</div>';
  }
}
</script>
</body>
</html>
"""


class MobileRequestHandler(BaseHTTPRequestHandler):
    shared_db: DatabaseManager = None

    def log_message(self, format, *args):
        pass

    def _get_db(self) -> DatabaseManager:
        if self.shared_db is not None:
            return self.shared_db
        return DatabaseManager()

    def _send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            db = self._get_db()

            if parsed.path == "/":
                body = MOBILE_HTML_TEMPLATE.encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            if parsed.path == "/api/catalogs":
                std_by_class = {
                    "Bárbaro":   {"Fuerza": 15, "Destreza": 13, "Constitución": 14, "Inteligencia": 10, "Sabiduría": 12, "Carisma": 8},
                    "Bardo":     {"Fuerza": 8,  "Destreza": 14, "Constitución": 12, "Inteligencia": 13, "Sabiduría": 10, "Carisma": 15},
                    "Brujo":     {"Fuerza": 8,  "Destreza": 14, "Constitución": 13, "Inteligencia": 12, "Sabiduría": 10, "Carisma": 15},
                    "Clérigo":   {"Fuerza": 14, "Destreza": 8,  "Constitución": 13, "Inteligencia": 10, "Sabiduría": 15, "Carisma": 12},
                    "Druida":    {"Fuerza": 8,  "Destreza": 12, "Constitución": 14, "Inteligencia": 13, "Sabiduría": 15, "Carisma": 10},
                    "Explorador":{"Fuerza": 12, "Destreza": 15, "Constitución": 13, "Inteligencia": 8,  "Sabiduría": 14, "Carisma": 10},
                    "Guerrero":  {"Fuerza": 15, "Destreza": 14, "Constitución": 13, "Inteligencia": 8,  "Sabiduría": 10, "Carisma": 12},
                    "Hechicero": {"Fuerza": 10, "Destreza": 13, "Constitución": 14, "Inteligencia": 8,  "Sabiduría": 12, "Carisma": 15},
                    "Mago":      {"Fuerza": 8,  "Destreza": 12, "Constitución": 13, "Inteligencia": 15, "Sabiduría": 14, "Carisma": 10},
                    "Monje":     {"Fuerza": 12, "Destreza": 15, "Constitución": 13, "Inteligencia": 10, "Sabiduría": 14, "Carisma": 8},
                    "Paladín":   {"Fuerza": 15, "Destreza": 10, "Constitución": 13, "Inteligencia": 8,  "Sabiduría": 12, "Carisma": 14},
                    "Pícaro":    {"Fuerza": 12, "Destreza": 15, "Constitución": 13, "Inteligencia": 14, "Sabiduría": 10, "Carisma": 8},
                }
                self._send_json({
                    "species_full": SPECIES_55E,
                    "backgrounds_full": BACKGROUNDS_55E,
                    "classes_full": CLASSES_55E,
                    "abilities": ABILITIES,
                    "skills": [sk[0] for sk in SKILLS_55E],
                    "languages": LANGUAGES_55E,
                    "instruments": MUSICAL_INSTRUMENTS,
                    "gaming_sets": GAMING_SETS,
                    "lineages": SPECIES_LINEAGES_55E,
                    "invocations": ELD_INVOCATIONS_55E,
                    "fighting_styles": FIGHTING_STYLES_55E,
                    "general_feats": GENERAL_FEATS_55E,
                    "epic_boons": EPIC_BOONS_55E,
                    "armors": list(ARMORS_CATALOG_55E.keys()),
                    "weapons": list(WEAPONS_CATALOG_55E.keys()),
                    "weapons_full": WEAPONS_CATALOG_55E,
                    "mounts": MOUNTS_CAPACITY_KG,
                    "items_by_cat": ITEMS_CATALOG_BY_CATEGORY,
                    "spells": Character55eRules.get_combined_spells_catalog(db),
                    "magic_attune": MAGIC_ITEMS_ATTUNEMENT_55E,
                    "std_scores": std_by_class
                })
                return

            if parsed.path == "/api/shop":
                self._send_json(self._build_shop_payload(db))
                return

            if parsed.path == "/api/live_table":
                self._send_json(db.get_live_table_state())
                return

            if parsed.path == "/api/characters":
                chars = db.get_all_characters()
                self._send_json([
                    {"id": c["id"], "name": c["name"], "level": c["level"], "species": c["species"], "char_class": c["char_class"]}
                    for c in chars
                ])
                return

            if parsed.path == "/api/character":
                qs = parse_qs(parsed.query)
                cid = int(qs.get("id", [0])[0])
                c = db.get_character_by_id(cid)
                if not c:
                    self._send_json({})
                    return
                self._send_json(self._format_char_for_mobile(c))
                return

            if parsed.path == "/api/search_pdf":
                qs = parse_qs(parsed.query)
                q = qs.get("q", [""])[0]
                self._send_json(db.search_manuals(q, limit=10))
                return
        except Exception as e:
            traceback.print_exc()
            self._send_json({"ok": False, "error": str(e)}, status=500)

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            raw = self.rfile.read(length).decode("utf-8")
            payload = json.loads(raw)
            db = self._get_db()

            if self.path == "/api/update_status":
                char = db.get_character_by_id(int(payload["id"]))
                if char:
                    stats = char.get("stats", {})
                    for k in ("hp_current", "hp_max", "hp_temp", "equipped_armor", "equipped_shield",
                              "armor_magic_bonus", "heroic_inspiration", "weapons", "coins",
                              "adventure_notes", "attuned_items"):
                        if k in payload:
                            stats[k] = payload[k]

                    scores = stats.get("scores", {ab: 10 for ab in ABILITIES})
                    mods = {ab: Character55eRules.get_modifier(int(scores.get(ab, 10))) for ab in ABILITIES}
                    stats["armor_class"] = Character55eRules.calculate_armor_class(
                        stats.get("equipped_armor", "Sin Armadura (10 + Des)"),
                        bool(stats.get("equipped_shield", False)),
                        int(stats.get("armor_magic_bonus", 0)),
                        mods
                    )
                    char["stats"] = stats
                    db.save_character(char)
                self._send_json({"ok": True})
                return

            if self.path == "/api/save_shard_character":
                saved_id = self._save_full_shard_progression(db, payload)
                self._send_json({"ok": True, "id": saved_id})
                return

            if self.path == "/api/update_spells":
                char = db.get_character_by_id(int(payload["id"]))
                if char:
                    stats = char.get("stats", {})
                    if "selected_cantrips" in payload:
                        stats["selected_cantrips"] = payload["selected_cantrips"]
                    if "selected_spells" in payload:
                        stats["selected_spells"] = payload["selected_spells"]
                    if "spent_spell_slots" in payload:
                        stats["spent_spell_slots"] = payload["spent_spell_slots"]
                    char["stats"] = stats
                    db.save_character(char)
                self._send_json({"ok": True})
                return

            if self.path == "/api/inventory_op":
                self._handle_inventory_operation(db, payload)
                self._send_json({"ok": True})
                return

            if self.path == "/api/shop_buy":
                ok, msg = self._handle_shop_buy(db, payload)
                self._send_json({"ok": ok, "msg": msg})
                return

            if self.path == "/api/shop_sell":
                ok, msg = self._handle_shop_sell(db, payload)
                self._send_json({"ok": ok, "msg": msg})
                return

            if self.path == "/api/rest_or_levelup":
                msg = self._handle_rest_or_levelup(db, payload)
                self._send_json({"ok": True, "msg": msg})
                return
        except Exception as e:
            traceback.print_exc()
            self._send_json({"ok": False, "error": str(e)}, status=500)

    def _build_shop_payload(self, db: DatabaseManager) -> dict:
        st = db.get_shop_state()
        preset = st.get("shop_preset", "Mercado Completo (Todo el Cap. 6)")
        mult = float(st.get("price_multiplier", 1.0))

        full_cats = dict(ITEMS_CATALOG_BY_CATEGORY)
        full_cats["Taberna, Comida y Posada (Pág. 231)"] = TAVERN_AND_SERVICES_55E

        if "Taberna" in preset:
            allowed_keys = ["Taberna, Comida y Posada (Pág. 231)"]
        elif "Herrería" in preset:
            allowed_keys = ["Armas (Capítulo 6)", "Armaduras y Escudos (Capítulo 6)"]
        elif "Bazar" in preset:
            allowed_keys = ["Contenedores y Recipientes", "Paquetes de Equipo (Auto-Desplegables)", "Equipo de Aventureros"]
        elif "Alquimia" in preset:
            allowed_keys = ["Munición, Canalizadores y Símbolos", "Herramientas, Instrumentos y Juegos", "Equipo de Aventureros"]
        elif "Establo" in preset:
            allowed_keys = ["Arreos, Sillas y Vehículos (Pág. 230)", "Contenedores y Recipientes"]
        else:
            allowed_keys = list(full_cats.keys())

        categories_out = {}
        for k in allowed_keys:
            raw_items = full_cats.get(k, [])
            processed = []
            for it in raw_items:
                cp_cost = Character55eRules.parse_price_to_cp(it.get("price", "0 po"), mult)
                if cp_cost <= 0 and "Objeto Mágico" in it.get("price", ""):
                    continue
                item_copy = dict(it)
                item_copy["cost_cp"] = cp_cost
                item_copy["adjusted_price_str"] = Character55eRules.format_cp_to_coins_str(cp_cost)
                processed.append(item_copy)
            if processed:
                categories_out[k] = processed

        return {
            "shop_name": st.get("shop_name", "Mercado del Pueblo"),
            "shop_preset": preset,
            "price_multiplier": mult,
            "is_open": bool(st.get("is_open", True)),
            "categories": categories_out
        }

    def _handle_shop_buy(self, db: DatabaseManager, p: dict) -> tuple:
        char = db.get_character_by_id(int(p["id"]))
        if not char:
            return False, "Personaje no encontrado."
        shop_st = db.get_shop_state()
        if not shop_st.get("is_open", True):
            return False, "El DM ha cerrado la tienda."

        item = p.get("item", {})
        qty = max(1, int(p.get("qty", 1)))
        unit_cp = int(item.get("cost_cp", 0))
        total_cost_cp = unit_cp * qty

        stats = char.get("stats", {})
        coins = stats.get("coins", {"cp": 0, "sp": 0, "gp": 0})
        player_total_cp = (int(coins.get("gp", 0)) * 100) + (int(coins.get("sp", 0)) * 10) + int(coins.get("cp", 0))

        if player_total_cp < total_cost_cp:
            needed_str = Character55eRules.format_cp_to_coins_str(total_cost_cp)
            have_str = Character55eRules.format_cp_to_coins_str(player_total_cp)
            return False, f"Monedas insuficientes: necesitas {needed_str} y tienes el equivalente a {have_str}."

        # Descontar monedas y devolver cambio optimizado en PO, PP y PC
        remaining_cp = player_total_cp - total_cost_cp
        new_gp = remaining_cp // 100
        rem = remaining_cp % 100
        new_sp = rem // 10
        new_cp = rem % 10
        stats["coins"] = {"cp": new_cp, "sp": new_sp, "gp": new_gp}

        # Si el peso es > 0 o es un contenedor/paquete, agregarlo al inventario elegido
        inv_key = "inventory_mount" if p.get("target") == "mount" else "inventory_char"
        inv_list = stats.setdefault(inv_key, [])

        if item.get("is_pack") and item["name"] in PACK_CONTENTS_55E:
            pk = PACK_CONTENTS_55E[item["name"]]
            cont = pk["container"]
            inv_list.append({
                "name": cont["name"], "qty": 1, "weight_kg": cont["weight_kg"],
                "is_container": True, "max_capacity_kg": cont.get("max_capacity_kg", 15.0),
                "ignore_contents_weight": False, "expanded": True,
                "contents": [dict(sub) for sub in pk["items"]]
            })
        elif float(item.get("weight_kg", 0.0)) > 0 or item.get("is_container") or "Estancia" not in item["name"]:
            inv_list.append({
                "name": item["name"], "qty": qty, "weight_kg": float(item.get("weight_kg", 0.0)),
                "is_container": bool(item.get("is_container", False)),
                "max_capacity_kg": item.get("max_capacity_kg"),
                "ignore_contents_weight": bool(item.get("ignore_contents_weight", False)),
                "expanded": True, "contents": []
            })

        char["stats"] = stats
        db.save_character(char)
        spent_str = Character55eRules.format_cp_to_coins_str(total_cost_cp)
        return True, f"🏪 ¡Compraste {qty}x {item['name']} por {spent_str}!\nSaldo restante: {new_gp} PO, {new_sp} PP, {new_cp} PC."

    def _handle_shop_sell(self, db: DatabaseManager, p: dict) -> tuple:
        """Vende 1 unidad de un objeto del inventario al 50% de su precio oficial del Capítulo 6 (Pág. 213)."""
        char = db.get_character_by_id(int(p["id"]))
        if not char:
            return False, "Personaje no encontrado."
        stats = char.get("stats", {})
        inv_key = "inventory_mount" if p.get("target") == "mount" else "inventory_char"
        inv_list = stats.get(inv_key, [])
        idx = int(p.get("index", -1))
        sub_idx = p.get("sub_index")

        if not (0 <= idx < len(inv_list)):
            return False, "Objeto no encontrado."

        if sub_idx is not None:
            contents = inv_list[idx].get("contents", [])
            if not (0 <= int(sub_idx) < len(contents)):
                return False, "Objeto interno no encontrado."
            target_obj = contents[int(sub_idx)]
        else:
            target_obj = inv_list[idx]

        obj_name = target_obj["name"]

        # Buscar precio oficial en el catálogo del Capítulo 6
        base_cp = 100  # 1 po por defecto si es un objeto personalizado
        for _, cat_items in ITEMS_CATALOG_BY_CATEGORY.items():
            found = next((x for x in cat_items if x["name"].lower() == obj_name.lower()), None)
            if found and found.get("price"):
                base_cp = Character55eRules.parse_price_to_cp(found["price"], 1.0)
                break

        half_cp = max(1, base_cp // 2)

        # Reducir cantidad en 1 o eliminar si quedaba 1
        if int(target_obj.get("qty", 1)) > 1:
            target_obj["qty"] = int(target_obj["qty"]) - 1
        else:
            if sub_idx is not None:
                inv_list[idx]["contents"].pop(int(sub_idx))
            else:
                inv_list.pop(idx)

        coins = stats.get("coins", {"cp": 0, "sp": 0, "gp": 0})
        total_cp = (int(coins.get("gp", 0)) * 100) + (int(coins.get("sp", 0)) * 10) + int(coins.get("cp", 0)) + half_cp
        stats["coins"] = {
            "gp": total_cp // 100,
            "sp": (total_cp % 100) // 10,
            "cp": total_cp % 10
        }
        char["stats"] = stats
        db.save_character(char)
        earned_str = Character55eRules.format_cp_to_coins_str(half_cp)
        return True, f"💰 Vendiste 1x '{obj_name}' por {earned_str} (50% del valor de compra según Pág. 213)."

    def _save_full_shard_progression(self, db: DatabaseManager, p: dict) -> int:
        cid = p.get("id")
        existing = db.get_character_by_id(int(cid)) if cid else None
        stats = existing.get("stats", Character55eRules.default_stats_payload()) if existing else Character55eRules.default_stats_payload()

        char_class = p.get("char_class", "Guerrero")
        species = p.get("species", "Humano")
        bg_name = p.get("background", "Acólito")
        level = max(1, min(20, int(p.get("level", 1))))

        c_info = CLASSES_55E.get(char_class, CLASSES_55E["Guerrero"])
        bg_info = BACKGROUNDS_55E.get(bg_name, BACKGROUNDS_55E["Acólito"])
        sp_info = SPECIES_55E.get(species, SPECIES_55E["Humano"])

        base_scores = p.get("base_scores", {ab: 10 for ab in ABILITIES})
        bg_bonuses = p.get("bg_bonuses", {"+1_a": "Ninguno", "+1_b": "Ninguno", "+1_c": "Ninguno"})
        prog_data = p.get("level_progression_choices", {})

        final_scores = dict(base_scores)
        for _, ab_chosen in bg_bonuses.items():
            if ab_chosen in final_scores:
                final_scores[ab_chosen] = min(20, final_scores[ab_chosen] + 1)

        for asi_lvl in Character55eRules.get_asi_levels(char_class):
            if asi_lvl <= level:
                for key_ab in (f"lvl{asi_lvl}_ab1", f"lvl{asi_lvl}_ab2"):
                    ab_up = prog_data.get(key_ab, "Ninguno")
                    if ab_up in final_scores:
                        final_scores[ab_up] = min(20, final_scores[ab_up] + 1)

        stats["base_scores"] = base_scores
        stats["scores"] = final_scores
        stats["bg_bonuses"] = bg_bonuses
        stats["level_progression_choices"] = prog_data
        stats["species_lineage"] = prog_data.get("species_lineage", "Ninguno")
        stats["human_extra_skill"] = prog_data.get("human_extra_skill", "Ninguna")
        stats["origin_feat"] = bg_info["feat"]
        stats["speed"] = "10,5 m" if "Elfo del Bosque" in stats["species_lineage"] else sp_info["speed"]
        stats["xp_current"] = int(p.get("xp_current", stats.get("xp_current", 0)))

        cls_skills = p.get("class_skill_choices", [])
        skilled_skills = p.get("skilled_feat_choices", [])
        bg_fixed = bg_info["skills"]
        extra_sk = [v for k, v in prog_data.items() if ("_sk" in k or "human_extra_skill" in k) and v not in ("Ninguna", "Ninguno", "")]
        exp_skills = [v for k, v in prog_data.items() if "_exp_" in k and v not in ("Ninguna", "Ninguno", "")]

        stats["class_skill_choices"] = cls_skills
        stats["skilled_feat_choices"] = skilled_skills
        stats["expertise_skills"] = exp_skills
        stats["instrument_choices"] = p.get("instrument_choices", [])
        stats["language_choices"] = p.get("language_choices", ["Común"])

        stats["saving_throws_prof"] = {ab: (ab in c_info["saves"]) for ab in ABILITIES}
        combined_sk = set(cls_skills + skilled_skills + bg_fixed + extra_sk + exp_skills)
        stats["skills_prof"] = {sk[0]: (sk[0] in combined_sk) for sk in SKILLS_55E}

        mods = {ab: Character55eRules.get_modifier(final_scores[ab]) for ab in ABILITIES}
        stats["armor_class"] = Character55eRules.calculate_armor_class(
            stats.get("equipped_armor", "Sin Armadura (10 + Des)"),
            bool(stats.get("equipped_shield", False)),
            int(stats.get("armor_magic_bonus", 0)),
            mods
        )

        max_hp = Character55eRules.calculate_max_hp(char_class, level, mods["Constitución"], bg_info["feat"], species)
        stats["hp_max"] = str(max_hp)
        if not existing:
            stats["hp_current"] = str(max_hp)
            stats["hit_dice_current"] = level

        subclass = "Se elige en Nivel 3"
        if level >= 3:
            chosen_sub = prog_data.get("lvl3_subclass", "Ninguna")
            subclass = chosen_sub if chosen_sub != "Ninguna" else c_info["subclasses"][0]

        return db.save_character({
            "id": cid,
            "name": p["name"],
            "player_name": p.get("player_name", ""),
            "species": species,
            "background": bg_name,
            "char_class": char_class,
            "subclass": subclass,
            "level": level,
            "stats": stats
        })

    def _handle_inventory_operation(self, db: DatabaseManager, p: dict):
        char = db.get_character_by_id(int(p["id"]))
        if not char:
            return
        stats = char.get("stats", {})
        op = p.get("op")

        if op == "set_mount":
            stats["mount_type"] = p.get("mount_type", "Sin Montura")
            char["stats"] = stats
            db.save_character(char)
            return

        inv_key = "inventory_char" if p.get("target") == "char" else "inventory_mount"
        inv_list = stats.setdefault(inv_key, [])

        if op == "add_catalog":
            tpl = p.get("item_tpl", {})
            qty = max(1, int(p.get("qty", 1)))
            cont_idx = p.get("container_idx")

            if tpl.get("is_pack") and tpl["name"] in PACK_CONTENTS_55E:
                pk = PACK_CONTENTS_55E[tpl["name"]]
                cont = pk["container"]
                inv_list.append({
                    "name": cont["name"], "qty": 1, "weight_kg": cont["weight_kg"],
                    "is_container": True, "max_capacity_kg": cont.get("max_capacity_kg", 15.0),
                    "ignore_contents_weight": False, "expanded": True,
                    "contents": [dict(sub) for sub in pk["items"]]
                })
            else:
                new_obj = {
                    "name": tpl["name"].strip(), "qty": qty, "weight_kg": float(tpl.get("weight_kg", 0.0)),
                    "is_container": bool(tpl.get("is_container", False)),
                    "max_capacity_kg": tpl.get("max_capacity_kg"),
                    "ignore_contents_weight": bool(tpl.get("ignore_contents_weight", False)),
                    "expanded": True, "contents": []
                }
                if cont_idx is not None and 0 <= cont_idx < len(inv_list):
                    inv_list[cont_idx].setdefault("contents", []).append({
                        "name": new_obj["name"], "qty": new_obj["qty"], "weight_kg": new_obj["weight_kg"]
                    })
                    inv_list[cont_idx]["expanded"] = True
                else:
                    inv_list.append(new_obj)

        elif op == "add_custom":
            inv_list.append({
                "name": p["name"], "qty": int(p.get("qty", 1)), "weight_kg": float(p.get("weight_kg", 0.0)),
                "is_container": bool(p.get("is_container", False)),
                "ignore_contents_weight": "bolsa de contención" in p["name"].lower(),
                "expanded": True, "contents": []
            })

        elif op == "toggle_expand":
            idx = int(p.get("index", -1))
            if 0 <= idx < len(inv_list):
                inv_list[idx]["expanded"] = not inv_list[idx].get("expanded", True)

        elif op == "remove":
            idx = int(p.get("index", -1))
            sub_idx = p.get("sub_index")
            if 0 <= idx < len(inv_list):
                if sub_idx is not None:
                    contents = inv_list[idx].get("contents", [])
                    if 0 <= int(sub_idx) < len(contents):
                        contents.pop(int(sub_idx))
                else:
                    inv_list.pop(idx)

        elif op == "transfer":
            idx = int(p.get("index", -1))
            other_key = "inventory_mount" if inv_key == "inventory_char" else "inventory_char"
            other_list = stats.setdefault(other_key, [])
            if 0 <= idx < len(inv_list):
                other_list.append(inv_list.pop(idx))

        char["stats"] = stats
        db.save_character(char)

    def _handle_rest_or_levelup(self, db: DatabaseManager, p: dict) -> str:
        char = db.get_character_by_id(int(p["id"]))
        if not char:
            return "Personaje no encontrado."
        stats = char.get("stats", {})
        lvl = int(char.get("level", 1))
        c_name = char.get("char_class", "Guerrero")
        hd_faces = CLASSES_55E.get(c_name, {}).get("hit_die", 8)
        con_score = int(stats.get("scores", {}).get("Constitución", 10))
        con_mod = Character55eRules.get_modifier(con_score)
        action = p.get("action")

        if action == "short_rest":
            avail = int(stats.get("hit_dice_current", lvl))
            spent = max(0, min(avail, int(p.get("dice_spent", 0))))
            roll_sum = int(p.get("roll_sum", 0))
            healed = max(spent, roll_sum + (spent * con_mod)) if spent > 0 else 0
            hp_max = int(stats.get("hp_max", 10))
            hp_curr = int(stats.get("hp_current", 10))
            new_hp = min(hp_max, hp_curr + healed)
            stats["hit_dice_current"] = avail - spent
            stats["hp_current"] = str(new_hp)
            if c_name == "Brujo":
                stats["spent_spell_slots"] = {}
            char["stats"] = stats
            db.save_character(char)
            return f"⛺ Descanso Corto: +{healed} PG curados ({hp_curr} → {new_hp}/{hp_max}). Dados restantes: {avail - spent}/{lvl}."

        if action == "long_rest":
            hp_max = int(stats.get("hp_max", 10))
            stats["hp_current"] = str(hp_max)
            stats["hp_temp"] = "0"
            stats["hit_dice_current"] = lvl
            stats["spent_spell_slots"] = {}
            if char.get("species") == "Humano":
                stats["heroic_inspiration"] = True
            char["stats"] = stats
            db.save_character(char)
            return f"🌙 Descanso Largo completado: PG ({hp_max}/{hp_max}), Dados de Golpe ({lvl}/{lvl}) y Espacios de Conjuro restaurados."

        if action == "level_up":
            if lvl >= 20:
                return "Ya estás en Nivel 20."
            next_lvl = lvl + 1
            die_val = int(p.get("die_val", (hd_faces // 2) + 1))
            hp_gain = max(1, die_val + con_mod)
            if char.get("species") == "Enano":
                hp_gain += 1
            if "Duro" in stats.get("origin_feat", ""):
                hp_gain += 2
            old_max = int(stats.get("hp_max", 10))
            old_curr = int(stats.get("hp_current", 10))
            stats["hp_max"] = str(old_max + hp_gain)
            stats["hp_current"] = str(old_curr + hp_gain)
            stats["hit_dice_current"] = min(next_lvl, int(stats.get("hit_dice_current", lvl)) + 1)
            min_xp = XP_THRESHOLDS_55E.get(next_lvl, 0)
            if int(stats.get("xp_current", 0)) < min_xp:
                stats["xp_current"] = min_xp
            char["level"] = next_lvl
            char["stats"] = stats
            db.save_character(char)
            return f"⬆️ ¡Subiste a Nivel {next_lvl}! (+{hp_gain} PG Máximos). Completa tus nuevas opciones en la pestaña '⚙️ Shard'."

        return "OK"

    def _format_char_for_mobile(self, c: dict) -> dict:
        stats = c.get("stats", {})
        lvl = int(c.get("level", 1))
        c_name = c.get("char_class", "Guerrero")
        sub_name = c.get("subclass", "")
        prof = Character55eRules.get_proficiency_bonus(lvl)
        scores = stats.get("scores", {ab: 10 for ab in ABILITIES})
        saves_prof = stats.get("saving_throws_prof", {})
        skills_prof = stats.get("skills_prof", {})
        exp_set = set(stats.get("expertise_skills", []))
        jack = (c_name == "Bardo" and lvl >= 2)
        prog_order = stats.get("level_progression_choices", {}).get("lvl1_order", "")

        mods = {ab: Character55eRules.get_modifier(int(scores.get(ab, 10))) for ab in ABILITIES}

        abilities_list = [
            {
                "name": ab, "score": scores.get(ab, 10),
                "mod": Character55eRules.format_mod(mods[ab]),
                "save": Character55eRules.format_mod(mods[ab] + (prof if saves_prof.get(ab) else 0))
            }
            for ab in ABILITIES
        ]

        skills_list = []
        skill_totals = {}
        for sk_name, ab in SKILLS_55E:
            base = mods.get(ab, 0)
            if sk_name in exp_set:
                tot = base + prof * 2
                pref = "★★ "
            elif skills_prof.get(sk_name):
                tot = base + prof
                pref = "✔ "
            elif jack:
                tot = base + (prof // 2)
                pref = "~"
            else:
                tot = base
                pref = ""
            if "Taumaturgo" in prog_order and sk_name in ("Conocimiento Arcano", "Religión"):
                tot += max(1, mods.get("Sabiduría", 0))
            elif "Naturalista" in prog_order and sk_name in ("Conocimiento Arcano", "Naturaleza"):
                tot += max(1, mods.get("Sabiduría", 0))
            skill_totals[sk_name] = tot
            skills_list.append({"name": f"{pref}{sk_name} ({ab[:3]})", "bonus": Character55eRules.format_mod(tot)})

        passives_text = (
            f"Percepción Pasiva: {10 + skill_totals.get('Percepción', 0)}  |  "
            f"Perspicacia: {10 + skill_totals.get('Perspicacia', 0)}  |  "
            f"Investigación: {10 + skill_totals.get('Investigación', 0)}"
        )

        weapons_out = []
        for w in stats.get("weapons", []):
            ab_u = w.get("ability", "Fuerza")
            ab_m = mods.get(ab_u, 0)
            m_name = w.get("mastery", "Ninguna")
            weapons_out.append({
                "name": w.get("name", ""), "damage": w.get("damage", ""),
                "atk": f"Atq {Character55eRules.format_mod(ab_m + prof)} | Daño {Character55eRules.format_mod(ab_m)}",
                "mastery": m_name, "mastery_desc": WEAPON_MASTERIES_55E.get(m_name, "")
            })

        slots_dict = Character55eRules.get_spell_slots_by_level(c_name, sub_name, lvl)
        always_prep = Character55eRules.get_always_prepared_spells(c_name, sub_name, lvl)
        sp_abil = CLASSES_55E.get(c_name, {}).get("spell_ability") or "Carisma"
        sp_mod = mods.get(sp_abil, 0)

        feats = Character55eRules.get_features_up_to_level(c["species"], c_name, sub_name, lvl)
        feat_lines = [
            f"=== RESUMEN DE RASGOS ({c_name.upper()} NIVEL {lvl}) ===",
            f"• Idiomas: {', '.join(stats.get('language_choices', ['Común']))}",
            f"• Dote de Origen: {stats.get('origin_feat', '')}"
        ]
        if stats.get("instrument_choices"):
            feat_lines.append(f"• Instrumentos: {', '.join(stats['instrument_choices'])}")
        if stats.get("expertise_skills"):
            feat_lines.append(f"• Pericia (★★): {', '.join(stats['expertise_skills'])}")
        att_active = [x for x in stats.get("attuned_items", []) if x]
        if att_active:
            feat_lines.append(f"• Sintonización Mágica ({len(att_active)}/3): {', '.join(att_active)}")
        feat_lines.append("")
        for t, d in feats:
            feat_lines.append(f"▸ {t}:\n  {d}")

        char_inv_tree = []
        char_total_kg = 0.0
        for it in stats.get("inventory_char", []):
            t_kg = Character55eRules.calculate_item_tree_weight(it)
            char_total_kg += t_kg
            item_copy = dict(it)
            item_copy["total_kg"] = t_kg
            char_inv_tree.append(item_copy)

        mount_inv_tree = []
        mount_total_kg = 0.0
        for it in stats.get("inventory_mount", []):
            t_kg = Character55eRules.calculate_item_tree_weight(it)
            mount_total_kg += t_kg
            item_copy = dict(it)
            item_copy["total_kg"] = t_kg
            mount_inv_tree.append(item_copy)

        mount_type = stats.get("mount_type", "Sin Montura")

        return {
            "id": c["id"], "name": c["name"], "player_name": c.get("player_name", ""),
            "level": lvl, "species": c["species"], "char_class": c_name,
            "subclass": sub_name, "background": c["background"], "prof": prof,
            "xp_current": int(stats.get("xp_current", 0)),
            "xp_next": Character55eRules.get_next_level_xp(lvl),
            "hit_dice": f"{stats.get('hit_dice_current', lvl)}/{lvl}",
            "hit_die_faces": CLASSES_55E.get(c_name, {}).get("hit_die", 8),
            "ac": stats.get("armor_class", 10),
            "init": Character55eRules.format_mod(mods.get("Destreza", 0)),
            "speed": stats.get("speed", "9 m"),
            "hp_curr": stats.get("hp_current", 10), "hp_max": stats.get("hp_max", 10), "hp_temp": stats.get("hp_temp", 0),
            "coins": stats.get("coins", {"cp": 0, "sp": 0, "gp": 0}),
            "abilities": abilities_list, "skills": skills_list, "passives_text": passives_text,
            "weapons": weapons_out,
            "spell_ability": sp_abil, "spell_dc": 8 + prof + sp_mod, "spell_atk": prof + sp_mod,
            "slots_dict": slots_dict, "always_prepared": always_prep,
            "max_cantrips": Character55eRules.get_cantrips_max(c_name, lvl, prog_order),
            "max_prepared": Character55eRules.get_prepared_spells_max(c_name, lvl),
            "max_spell_lvl": Character55eRules.get_max_spell_level(c_name, lvl),
            "features_summary": "\n".join(feat_lines),
            "char_inv_tree": char_inv_tree,
            "char_total_kg": round(char_total_kg, 2),
            "char_max_kg": Character55eRules.get_carrying_capacity_kg(int(scores.get("Fuerza", 10)), c["species"]),
            "mount_type": mount_type,
            "mount_inv_tree": mount_inv_tree,
            "mount_total_kg": round(mount_total_kg, 2),
            "mount_max_kg": MOUNTS_CAPACITY_KG.get(mount_type, 0.0),
            "stats": stats
        }


class MobileCompanionServer:
    def __init__(self, db: DatabaseManager = None, port=8080):
        self.db = db or DatabaseManager()
        self.port = port
        self.server = None

    def get_local_ip(self) -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def start(self) -> str:
        if self.server is None:
            MobileRequestHandler.shared_db = self.db
            # Si el puerto 8080 está ocupado en esta PC, prueba automáticamente 8081, 8082, etc.
            for candidate_port in range(self.port, self.port + 15):
                try:
                    self.server = ThreadingHTTPServer(("0.0.0.0", candidate_port), MobileRequestHandler)
                    self.port = candidate_port
                    break
                except OSError:
                    continue
            threading.Thread(target=self.server.serve_forever, daemon=True).start()
        return f"http://{self.get_local_ip()}:{self.port}"

    def generate_qr_pil(self, url: str, box_size: int = 6) -> Image.Image:
        qr = qrcode.QRCode(version=1, box_size=box_size, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        return qr.make_image(fill_color="black", back_color="white").convert("RGB")