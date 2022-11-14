import React from 'react';

class TextInput  extends React.Component {
  constructor(props) {
    super(props);
    this.changeValue = this.changeValue.bind(this);
    this.state = {text_value: props.value}
  }

  changeValue (e) {
    this.setState({text_value: e.target.value});
  }
  
  render() {
    const text_value = this.state.text_value;
    const inp_type = this.props.type || 'text';
    const title = this.props.title;
    return <fieldset>
      <legend>{title}</legend>
      <input type={inp_type} value={text_value} onChange={this.changeValue}/>
    </fieldset>
  }
}

class UrlCreator extends React.Component {
  constructor(props) {
      super(props);
      this.createUrl = this.createUrl.bind(this);
      this.state = {
          target_url: '',
          email_address: props.email
      };
  }

  createUrl (e) {
    console.log(this.state)
  }

  render() {
    const target_url = this.state.target_url;
    const email_address = this.state.email_address;
    return <div className="url-creator">
      <TextInput value={target_url} title="Target url"/>
      <TextInput value={email_address} type="email" title="User email" />
      <div>
        <button onClick={this.createUrl}>Shorten</button>
      </div>
    </div>;
  }
}

export default UrlCreator;
