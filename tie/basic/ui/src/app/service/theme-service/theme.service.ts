import { BehaviorSubject } from 'rxjs';

import { Injectable } from '@angular/core';
import { MonacoEditorOptions } from 'src/app/models/monaco-editor-options.interface';

/**
 * The default options are mostly set in the app.module.ts file preloaded when the editor is created, where as these
 * are loaded when the editor is actually created which keeps things simpler.
 */
@Injectable({
    providedIn: 'root',
})
export class ThemeService {
    private _monacoEditorOptions: MonacoEditorOptions = {
        automaticLayout: true, // needed if you want to resize the editor
        contextmenu: true,
        language: 'json',
        minimap: { enabled: false },
        readOnly: false,
        scrollBeyondLastLine: false,
        theme: 'vs-light',
        wordWrap: 'on',
    };
    private _monacoEditorOptionsReadOnly: MonacoEditorOptions = {
        ...this._monacoEditorOptions,
        contextmenu: false,
        readOnly: true,
    };
    private _monacoEditorOptionsWorkBench: MonacoEditorOptions = {
        ...this._monacoEditorOptions,
        automaticLayout: true,
        contextmenu: true,
        language: 'sql',
        readOnly: false,
    };

    private _theme = new BehaviorSubject<'light' | 'dark'>('light');
    public theme$ = this._theme.asObservable();

    private _editorOptions = new BehaviorSubject<MonacoEditorOptions>(this._monacoEditorOptions);
    public editorOptions$ = this._editorOptions.asObservable();

    private _editorOptionsReadOnly = new BehaviorSubject<MonacoEditorOptions>(
        this._monacoEditorOptionsReadOnly,
    );
    public editorOptionsReadOnly$ = this._editorOptionsReadOnly.asObservable();

    private _editorOptionsWorkBench = new BehaviorSubject<MonacoEditorOptions>(
        this._monacoEditorOptionsWorkBench,
    );
    public editorOptionsWorkBench$ = this._editorOptionsWorkBench.asObservable();

    setTheme(theme: 'light' | 'dark') {
        this._theme.next(theme);

        this._monacoEditorOptions = {
            ...this._monacoEditorOptions,
            theme: theme === 'light' ? 'vs-light' : 'vs-dark',
        };
        this._monacoEditorOptionsReadOnly = {
            ...this._monacoEditorOptionsReadOnly,
            theme: theme === 'light' ? 'vs-light' : 'vs-dark',
        };
        this._monacoEditorOptionsWorkBench = {
            ...this._monacoEditorOptionsWorkBench,
            theme: theme === 'light' ? 'vs-light' : 'vs-dark',
        };
        this._editorOptions.next(this._monacoEditorOptions);
        this._editorOptionsReadOnly.next(this._monacoEditorOptionsReadOnly);
        this._editorOptionsWorkBench.next(this._monacoEditorOptionsWorkBench);
    }
}
