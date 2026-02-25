export interface MonacoEditorOptions {
    theme: 'vs-dark' | 'vs-light';
    language: 'json' | 'sql';
    readOnly: boolean;
    automaticLayout?: boolean; // needed if you want to resize the editor
    scrollBeyondLastLine: boolean;
    wordWrap: 'on' | 'off';
    minimap: { enabled: boolean };
    contextmenu: boolean;
}
