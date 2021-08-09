"use strict";
// Copyright: Ankitects Pty Ltd and contributors
// License: GNU AGPL, version 3 or later; http://www.gnu.org/licenses/agpl.html
var SyncState;
(function (SyncState) {
    SyncState[SyncState["NoChanges"] = 0] = "NoChanges";
    SyncState[SyncState["Normal"] = 1] = "Normal";
    SyncState[SyncState["Full"] = 2] = "Full";
})(SyncState || (SyncState = {}));
function updateSyncColor(state) {
    const elem = document.getElementById("sync");
    switch (state) {
        case SyncState.NoChanges:
            elem.classList.remove("full-sync", "normal-sync");
            break;
        case SyncState.Normal:
            elem.classList.add("normal-sync");
            elem.classList.remove("full-sync");
            break;
        case SyncState.Full:
            elem.classList.add("full-sync");
            elem.classList.remove("normal-sync");
            break;
    }
}
//# sourceMappingURL=data:application/json;base64,eyJ2ZXJzaW9uIjozLCJmaWxlIjoidG9vbGJhci5qcyIsInNvdXJjZVJvb3QiOiIiLCJzb3VyY2VzIjpbIi4uLy4uLy4uLy4uLy4uLy4uLy4uLy4uL3F0L2FxdC9kYXRhL3dlYi9qcy90b29sYmFyLnRzIl0sIm5hbWVzIjpbXSwibWFwcGluZ3MiOiI7QUFBQSxnREFBZ0Q7QUFDaEQsK0VBQStFO0FBRS9FLElBQUssU0FJSjtBQUpELFdBQUssU0FBUztJQUNWLG1EQUFhLENBQUE7SUFDYiw2Q0FBTSxDQUFBO0lBQ04seUNBQUksQ0FBQTtBQUNSLENBQUMsRUFKSSxTQUFTLEtBQVQsU0FBUyxRQUliO0FBRUQsU0FBUyxlQUFlLENBQUMsS0FBZ0I7SUFDckMsTUFBTSxJQUFJLEdBQUcsUUFBUSxDQUFDLGNBQWMsQ0FBQyxNQUFNLENBQUMsQ0FBQztJQUM3QyxRQUFRLEtBQUssRUFBRTtRQUNYLEtBQUssU0FBUyxDQUFDLFNBQVM7WUFDcEIsSUFBSSxDQUFDLFNBQVMsQ0FBQyxNQUFNLENBQUMsV0FBVyxFQUFFLGFBQWEsQ0FBQyxDQUFDO1lBQ2xELE1BQU07UUFDVixLQUFLLFNBQVMsQ0FBQyxNQUFNO1lBQ2pCLElBQUksQ0FBQyxTQUFTLENBQUMsR0FBRyxDQUFDLGFBQWEsQ0FBQyxDQUFDO1lBQ2xDLElBQUksQ0FBQyxTQUFTLENBQUMsTUFBTSxDQUFDLFdBQVcsQ0FBQyxDQUFDO1lBQ25DLE1BQU07UUFDVixLQUFLLFNBQVMsQ0FBQyxJQUFJO1lBQ2YsSUFBSSxDQUFDLFNBQVMsQ0FBQyxHQUFHLENBQUMsV0FBVyxDQUFDLENBQUM7WUFDaEMsSUFBSSxDQUFDLFNBQVMsQ0FBQyxNQUFNLENBQUMsYUFBYSxDQUFDLENBQUM7WUFDckMsTUFBTTtLQUNiO0FBQ0wsQ0FBQyIsInNvdXJjZXNDb250ZW50IjpbIi8vIENvcHlyaWdodDogQW5raXRlY3RzIFB0eSBMdGQgYW5kIGNvbnRyaWJ1dG9yc1xuLy8gTGljZW5zZTogR05VIEFHUEwsIHZlcnNpb24gMyBvciBsYXRlcjsgaHR0cDovL3d3dy5nbnUub3JnL2xpY2Vuc2VzL2FncGwuaHRtbFxuXG5lbnVtIFN5bmNTdGF0ZSB7XG4gICAgTm9DaGFuZ2VzID0gMCxcbiAgICBOb3JtYWwsXG4gICAgRnVsbCxcbn1cblxuZnVuY3Rpb24gdXBkYXRlU3luY0NvbG9yKHN0YXRlOiBTeW5jU3RhdGUpIHtcbiAgICBjb25zdCBlbGVtID0gZG9jdW1lbnQuZ2V0RWxlbWVudEJ5SWQoXCJzeW5jXCIpO1xuICAgIHN3aXRjaCAoc3RhdGUpIHtcbiAgICAgICAgY2FzZSBTeW5jU3RhdGUuTm9DaGFuZ2VzOlxuICAgICAgICAgICAgZWxlbS5jbGFzc0xpc3QucmVtb3ZlKFwiZnVsbC1zeW5jXCIsIFwibm9ybWFsLXN5bmNcIik7XG4gICAgICAgICAgICBicmVhaztcbiAgICAgICAgY2FzZSBTeW5jU3RhdGUuTm9ybWFsOlxuICAgICAgICAgICAgZWxlbS5jbGFzc0xpc3QuYWRkKFwibm9ybWFsLXN5bmNcIik7XG4gICAgICAgICAgICBlbGVtLmNsYXNzTGlzdC5yZW1vdmUoXCJmdWxsLXN5bmNcIik7XG4gICAgICAgICAgICBicmVhaztcbiAgICAgICAgY2FzZSBTeW5jU3RhdGUuRnVsbDpcbiAgICAgICAgICAgIGVsZW0uY2xhc3NMaXN0LmFkZChcImZ1bGwtc3luY1wiKTtcbiAgICAgICAgICAgIGVsZW0uY2xhc3NMaXN0LnJlbW92ZShcIm5vcm1hbC1zeW5jXCIpO1xuICAgICAgICAgICAgYnJlYWs7XG4gICAgfVxufVxuIl19